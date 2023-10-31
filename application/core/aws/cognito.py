import boto3
from application.core.configuration_loader import get_configuration


def authorizer_get_data(event, attribute):
    """Recover user_name token

    :param event: event request object api gateway
    :return: String user_name.
    """
    return event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get(f'{attribute}', None)


def cognito_get_user(username):
    """Get user information from cognito user pool by username.

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to get the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    try:
        response = client.admin_get_user(
            UserPoolId=configuration.COGNITO_USER_POOL_ID,
            Username=username.lower()
        )

        return response
    except Exception as e:
        print(f'[AWS: COGNITO] ADMIN_GET_USER > Exception: {e}')

    return None


def cognito_create_user(username, password, user_attributes, validation_data):
    """Registers the user in the specified user pool and creates a user
     name, password, and user attributes.

    :param username: string
    :param password: string
    :param user_attributes: list
    :param validation_data: list
    :return: Represents the response (dict) from the server to the request
    to create the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    response = client.sign_up(
        ClientId=configuration.COGNITO_USER_POOL_CLIENT_ID,
        Username=username,
        Password=password,
        UserAttributes=user_attributes,
        ValidationData=validation_data
    )

    return response


def cognito_admin_create_user(username, password, user_attributes, client_metadata):
    """Registers the user in the specified user pool and creates a user
     name, password, and user attributes with admin flow.

    :param username: string
    :param password: string
    :param user_attributes: list
    :param validation_data: list
    :return: Represents the response (dict) from the server to the request
    to create the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')


    response = client.admin_create_user(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username,
        TemporaryPassword=password,
        DesiredDeliveryMediums=["EMAIL"],
        UserAttributes=user_attributes,
        ClientMetadata=client_metadata
    )

    return response


def cognito_delete_user(username):
    """Delete user in Cognito

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to delete the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    response = client.admin_delete_user(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower()
    )

    return response


def cognito_get_user_groups(username):
    """Get user groups in Cognito

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to get the user groups.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    response = client.admin_list_groups_for_user(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower()
    )

    return response

def cognito_set_user_group(username, group):
    """Set user groups in Cognito

    :param username: string
    :param groups: string list []
    :return: Represents the response (dict) from the server to the request
    to get the user groups.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')


    response = client.admin_add_user_to_group(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower(),
        GroupName=group
    )

    return response

def cognito_del_user_group(username, group):
    """Del user from groups in Cognito

    :param username: string
    :param groups: string list []
    :return: Represents the response (dict) from the server to the request
    to get the user groups.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')


    response = client.admin_remove_user_from_group(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower(),
        GroupName=group
    )

    return response


def cognito_admin_reset_user_password(username):
    """Resets  user password, so user will recieve a email for changing the password.

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to disable the user.
    """

    configuration = get_configuration()

    client = boto3.client('cognito-idp')

    response = client.admin_reset_user_password(

        Username=username.lower(),
        UserPoolId=configuration.COGNITO_USER_POOL_ID
    )
    return response


def cognito_update_user_attributes(username, user_attributes):
    """Delete user in Cognito

    :param username: string
    :param user_attributes: list
    :return: Represents the response (dict) from the server to the request
    to update the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    response = client.admin_update_user_attributes(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower(),
        UserAttributes=user_attributes
    )

    return response


def cognito_disable_user(username):
    """Disable user in Cognito

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to disable the user.
    """

    configuration = get_configuration()
    client = boto3.client('cognito-idp')

    response = client.admin_disable_user(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower()
    )

    return response


def cognito_enable_user(username):
    """Enable user in Cognito

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to disable the user.
    """

    configuration = get_configuration()

    client = boto3.client('cognito-idp')

    response = client.admin_enable_user(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower()
    )

    return response


def cognito_revoke_session(username):
    """Enable user in Cognito

    :param username: string
    :return: Empty dict {}.
    """

    configuration = get_configuration()

    client = boto3.client('cognito-idp')

    response = client.admin_user_global_sign_out(
        UserPoolId=configuration.COGNITO_USER_POOL_ID,
        Username=username.lower()
    )

    return response


def cognito_link_provider_for_user(source_provider_name, source_provider_user_id, destination_username):
    """Links an existing user account in a user pool (DestinationUser ) to an identity
    from an external identity provider (SourceUser ) based on a specified attribute name
    and value from the external identity provider. This allows you to create a link from
    the existing user account to an external federated user identity that has not yet been
    used to sign in, so that the federated user identity can be used to sign in as the
    existing user account.

    :param username: string
    :return: Represents the response (dict) from the server to the request
    to get the user.
    """

    configuration = get_configuration()

    client = boto3.client('cognito-idp')

    try:
        response = client.admin_link_provider_for_user(
            UserPoolId=configuration.COGNITO_USER_POOL_ID,
            SourceUser={
                'ProviderName': source_provider_name,
                'ProviderAttributeName': 'Cognito_Subject',
                'ProviderAttributeValue': source_provider_user_id
            },
            DestinationUser={
                'ProviderName': 'Cognito',
                # 'ProviderAttributeName': 'username',
                'ProviderAttributeValue': destination_username
            },
        )

        return response
    except Exception as e:
        print(f'[AWS: COGNITO] ADMIN_LINK_PROVIDER_FOR_USER > Exception: {e}')

def cognito_get_all_groups():
    """List all cognito groups

    :return: string list [].
    """

    configuration = get_configuration()

    client = boto3.client('cognito-idp')

    response = client.list_groups(
        UserPoolId=configuration.COGNITO_USER_POOL_ID
    )

    return response
