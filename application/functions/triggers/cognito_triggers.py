def pre_verification_trigger(event, context):
    """This trigger is invoked when a user submits registration information so
    that you can perform a custom validation to accept or deny the registration
    request. In our case we create the cognito user in the database.

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.core.mail.mail_handler import get_cognito_confirmation_email, get_cognito_invitation_email, get_cognito_forgot_email

    """
    [triggerSource] EVENTS
    > 'CustomMessage_SignUp':                   Custom message – To send the confirmation code post sign-up.
    > 'CustomMessage_AdminCreateUser':          CustomMessage_AdminCreateUser
    > 'CustomMessage_ResendCode':               CustomMessage_ResendCode
    > 'CustomMessage_ForgotPassword':           Custom message – To send the confirmation code for Forgot Password request.
    > 'CustomMessage_UpdateUserAttribute':      Custom message – When a user's email or phone number is changed, this trigger sends a verification code automatically to the user. Cannot be used for other attributes.
    > 'CustomMessage_VerifyUserAttribute':      Custom message – This trigger sends a verification code to the user when they manually request it for a new email or phone number.
    > 'CustomMessage_Authentication':           Custom message – To send MFA code during authentication.
    """

    print('[SIGN UP] EVENT', event)
    print('[SIGN UP] CONTEXT', context)

    try:
        username = event.get('userName')
        username_parameter = event.get('request').get('usernameParameter')
        code_parameter = event.get('request').get('codeParameter')
        email = event.get('request').get('userAttributes').get('email')
        language = event.get('request').get('userAttributes').get('custom:language', 'EN-en')

        _context = {}

        if event.get('triggerSource') == 'CustomMessage_SignUp':
            _message, _subject = get_cognito_confirmation_email(username=username, email=email, code=code_parameter, language=language)
            _context.update({
                'emailSubject': _subject,
                'emailMessage': _message
            })

        # TODO: Revision
        if event.get('triggerSource') == 'CustomMessage_AdminCreateUser':
            print('Llega')
            _user_name = event.get('request').get('clientMetadata').get('user_name')
            _admin_name = event.get('request').get('clientMetadata').get('admin_name')
            _message, _subject = get_cognito_invitation_email(username=username_parameter, user_name=_user_name, admin_name=_admin_name, code=code_parameter, language=language)
            print('Peta')
            _context.update({
                'emailSubject': _subject,
                'emailMessage': _message
            })

        if event.get('triggerSource') == 'CustomMessage_ForgotPassword':
            _message, _subject = get_cognito_forgot_email(username=username, email=email, code=code_parameter, language=language)
            _context.update({
                'emailSubject': _subject,
                'emailMessage': _message
            })

        if _context:
            event.get('response').update(_context)

    except Exception as e:
        # TODO: Include handler error triggers
        raise Exception(e)

    print('[SIGN UP] EVENT', event)
    return event


# TODO: Revise
def pre_sign_up_trigger(event, context):
    """This trigger is invoked prior to token generation, allowing you to
     customize identity token claims. In our case, the user's role and
     permissions are added.

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """
    from application.core.aws.cognito import cognito_get_user, cognito_link_provider_for_user

    print('[SIGN UP] EVENT', event)
    print('[SIGN UP] CONTEXT', context)

    # Control only form external providers
    if event.get('triggerSource', None) == 'PreSignUp_ExternalProvider':

        try:
            source_provider_name, source_provider_user_id = event.get('userName').split('_')
            print('[SOURCE] PROVIDER_NAME', source_provider_name)
            print('[SOURCE] PROVIDER_USER_ID', source_provider_user_id)

            user_email = event.get('request').get('userAttributes').get('email', None)

            destination_user = cognito_get_user(user_email)

            if destination_user:
                # CHECK Confirmation status
                email_verified = next((t.get('Value') for t in destination_user.get('UserAttributes') if t.get('Name') == 'email_verified'), None)

                if not email_verified or email_verified == 'false':
                    raise Exception("PROVIDER_TO_USER_NOT_CONFIRMED")

                # LINK User from user pool
                print('[DESTINATION] COGNITO_USERNAME', destination_user.get('Username'))
                cognito_link_provider_for_user(
                    source_provider_name=source_provider_name,
                    source_provider_user_id=source_provider_user_id,
                    destination_username=destination_user.get('Username')
                )

                return event
            else:
                raise Exception("PROVIDER_NOT_REGISTER")
        except Exception as e:
            raise Exception("PROVIDER_AUTH_ERROR")

    return event


def pre_token_generation_trigger(event, context):
    """This trigger is invoked prior to token generation, allowing you to
     customize identity token claims. In our case, the user's role and
     permissions are added.

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """
    import json
    from application.functions.db.database_controller import get_user_permissions

    auth_flow = True \
        if (event.get('triggerSource') == 'TokenGeneration_Authentication' or event.get('triggerSource') == 'TokenGeneration_HostedAuth') \
        else False

    permissions = {}


    try:
        # Recover email user that try login
        _user_email = event.get('request').get('userAttributes').get('email', None)
        print('[PRE TOKEN] User email', _user_email)

        if _user_email:
            # Recover permissions from this user
            user_id = get_user_permissions(email=_user_email, update_access=auth_flow)
            #user_id, permissions = get_user_permissions(email=_user_email, update_access=auth_flow)
            print('[PRE TOKEN] PERMISSIONS', permissions)

            # Normalize data to include in token data
            #permissions = json.dumps(permissions, separators=(',', ':')).replace('\"', "'")
    except Exception as e:
        # TODO: Include handler error triggers
        print("[PRE TOKEN] EXCEPTION", e)

    event['response']['claimsOverrideDetails'] = {
        'claimsToAddOrOverride': {
            'user_id': user_id#,
            #'access': permissions
        }
    }

    return event


