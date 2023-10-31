import json
from sqlalchemy.event import listens_for

from application.controllers.companies_controller import post_companies
from application.core.auth.check_permissions_readonly import CheckReadOnly
from application.core.aws import cognito_create_user, cognito_admin_create_user, cognito_update_user_attributes, \
    cognito_revoke_session, cognito_enable_user, cognito_disable_user, authorizer_get_data
from application.core.configuration_loader import get_configuration
from application.core.http import HTTPRouter, get_request_query_parameter, jsonify, HTTPError
from application.core.http.http_functions import get_request_path_parameter
from application.core.sql import db
from application.core.sql.defaults import default_list, default_get, default_create, default_update, default_insert, default_delete
from application.models.companies_model import Companies
from application.models.resources_model import Countries
from application.models.users_model import Users, Roles, UsersResourcesJobs, UsersModulesPermissions
from application.services.recaptcha_service import verify_recaptcha_token
from application.core.aws.cognito import cognito_admin_reset_user_password, cognito_del_user_group, cognito_get_all_groups, cognito_get_user_groups, cognito_set_user_group, cognito_update_user_attributes
from application.services.zoho_service import zoho_check_information

# ENTITY CONTROLLER: Users =============================================================================================


@HTTPRouter.route('api/register', 'POST')
@CheckReadOnly()
def post_users(event, context):
    recaptcha_token = event.get('headers').get('Authorization')
    verify_recaptcha_token(recaptcha_token)
    body = json.loads(event.get('body', None))

    if not body:
        raise HTTPError(404, 'Body not correct')


    event.update({'body': json.dumps(_user)})

    return post_users(event, context)


@HTTPRouter.route('api/user', 'GET')
def get_user_company(event, context):
    request_user = authorizer_get_data(event, 'email')

    _schema = {'relations': {
        'company': {'exclude': []},
        'role': {'relations': {'access': {'relations': {
            'module': {'exclude': ['policies']},
            'permission': {'exclude': ['policies']}
        }}}},
        'policies': {'relations': {
            'module': {'exclude': ['access']},
            'permission': {'exclude': ['access']}
        }}
    }}
    return default_get(model_class=Users, query_where={'email': request_user}, schema=_schema)




@HTTPRouter.route('api/users', 'GET')
def get_users(event, context):
    company_status = get_request_query_parameter(
        param_key='company_status', request=event, default_value=None)
    company_commodities = get_request_query_parameter(
        param_key='company_commodities', request=event, default_value=None)
    is_master = get_request_query_parameter(
        param_key='is_master', request=event, default_value=None)
    crFilter = get_request_query_parameter(param_key='crStatus', request=event, default_value=None)
    roiFilter = get_request_query_parameter(param_key='roiStatus', request=event, default_value=None)
    invited_by_user_id = get_request_query_parameter(param_key='invited_by_user_id', request=event, default_value=None)
    typeCompanyFilter = get_request_query_parameter(param_key='typeCompany', request=event, default_value=None)

    _schema = {'relations': {'company': {'relations': {
        'services': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'commodities': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'sections_profile': {'include': ['id', 'name', 'tag']},
        'profile':{'exclude' : ['created_on', 'updated_on']}
    }}}}
    _filter = {}
    if company_commodities:
        _commodities = company_commodities.split(',')
        _filter.update(
            {'company___commodities___commodity_name__in': _commodities})

    if company_status:
        _filter.update(
            {'company___status__exact': company_status if company_status != 'none' else None})

    if is_master:
        _filter.update({'is_master__exact': is_master})
    
    if crFilter:
        _filter.update({'company___profile___status__exact': crFilter})

    if roiFilter:
        _filter.update({'company___status__exact': roiFilter})
    if invited_by_user_id:
        _filter.update({'company___invited_by_user_id__exact': invited_by_user_id})
    if typeCompanyFilter:
        _filter.update({'company___type__exact': typeCompanyFilter})

    return default_list(model_class=Users, query_where=_filter, schema=_schema)


@HTTPRouter.route('api/users', 'POST')
@CheckReadOnly()
def post_users(event, context):
    import re
    body = json.loads(event.get('body', None))

    password = body.get('password', None)

    user = {
        'role_id': 2,  # DEFAULT ROLE (company_guest)
        'country_id': body.get('country_id', None),
        'company_id': body.get('company_id', None),
        'email': body.get('email', None),
        'first_name': body.get('first_name', ''),
        'last_name': body.get('last_name', ''),
        'phone': body.get('phone', None),
        'job_title': body.get('job_title', None),
        'language': body.get('language', 'en-EN'),
        'is_master': True if body.get('company_id', None) else False
    }

    # Normalize fields
    user.update({'email': user.get('email').lower()})
    user.update({'phone': re.sub('[^0-9\+]', '', user.get('phone'))})

    # Generate attributes cognito
    user_attributes = [
        {'Name': 'email', 'Value': user.get('email')},
        {'Name': 'name',
            'Value': f"{user.get('first_name')} {user.get('last_name')}"},
        {'Name': 'phone_number', 'Value': user.get('phone')},
        {'Name': 'custom:language', 'Value': user.get('language')}
    ]

    validation_data = [{'Name': 'email', 'Value': user.get('email')}]
    cognito_create_user(user.get('email'), password,
                        user_attributes, validation_data)

    return default_create(model_or_constructor=Users, dict_=user, post_create_fn=_post_user_management)


@HTTPRouter.route('api/users/employees', 'POST')
@CheckReadOnly()
def post_users_employees(event, context):
    import re
    configuration = get_configuration()
    body = json.loads(event.get('body', None))

    password = body.get('password', None)

    user = {
        'role_id': body.get('role_id'),
        'country_id': body.get('country_id', None),
        'company_id': body.get('company_id', None),
        'email': body.get('email', None),
        'first_name': body.get('first_name', ''),
        'last_name': body.get('last_name', ''),
        'phone': body.get('phone', None),
        'job_title': body.get('job_title', None),
        'language': body.get('language', 'en-EN'),
        'is_master': False
    }

    # Normalize fields
    user.update({'email': user.get('email').lower()})
    user.update({'phone': re.sub('[^0-9\+]', '', user.get('phone'))})

    admin_user = Users.query.filter_by(
        company_id=user.get('company_id'), is_master=True).first()

    # Generate attributes cognito
    # TODO: Revise auto email confirmation
    user_attributes = [
        {'Name': 'email', 'Value': user.get('email')},
        {'Name': 'name',
            'Value': f"{user.get('first_name')} {user.get('last_name')}"},
        {'Name': 'phone_number', 'Value': user.get('phone')},
        {'Name': 'email_verified', 'Value': 'true'},
        {'Name': 'custom:language', 'Value': user.get('language')}
    ]

    client_metadata = {
        'user_name': user.get('first_name').title(),
        'admin_name': f"{admin_user.first_name} {admin_user.last_name}".title()
    }
    cognito_admin_create_user(
        user.get('email'), password, user_attributes, client_metadata)
    
    company = Companies.query.filter_by(id=user.get('company_id')).first()
    if company.is_inspection_company:
        cognito_set_user_group(user.get('email'), configuration.COGNITO_SERVICE_PROVIDER_INSPECTION_GROUP)

    return default_create(model_or_constructor=Users, dict_=user)


@HTTPRouter.route('api/users', 'PATCH')
@CheckReadOnly()
def patch_users(event, context):

    access_info = authorizer_get_data(event, 'access')
    user_id = authorizer_get_data(event, 'user_id')
    access_info_json = json.loads(access_info.replace("'", '"'))

    data = json.loads(event.get('body', None))

    if not user_id:
        raise HTTPError(401, f'No valid token provided.')

    user_id = int(user_id)

    roles = [
        'system_administrator',
        'company_administrator'
    ]

    if access_info_json['role']['name'] not in roles and user_id != data['id']:
        raise HTTPError(401, f'Not authorized.')

    _schema = {'relations': {'company': { 'relations': {
        'services': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'commodities': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'sections_profile': {'include': ['id', 'name', 'tag']}
    }}}}

    # TODO: Update language requiere update attribute cognito
    
    if 'groups' in data:
        set_user_groups(data['id'], data['groups'])
        del data['groups']

    return default_update(model_class=Users, _dict=data, schema=_schema)


def set_user_groups(user_id, new_groups):
    username = Users.query.filter_by(id=user_id).first().email
    old_groups_name_list = [x['GroupName'] for x in cognito_get_user_groups(username)['Groups']]
    for old_group_name in old_groups_name_list:
        if old_group_name not in new_groups:
            cognito_del_user_group(username, old_group_name)
    for new_group_name in new_groups:
        if new_group_name not in old_groups_name_list:
            cognito_set_user_group(username, new_group_name)


@HTTPRouter.route('api/user/crm', 'PATCH')
@CheckReadOnly()
def get_user_crm(event, context):

    access_info = authorizer_get_data(event, 'access')
    access_info_json = json.loads(access_info.replace("'", '"'))
    user_id = authorizer_get_data(event, 'user_id')
    
    if not user_id:
        raise HTTPError(401, f'No valid token provided.')
    
    user_id = int(user_id)

    user = json.loads(event.get('body', None))

    roles = [
        'system_administrator',
        'company_administrator',
        'platform_admin'
    ]

    if access_info_json['role']['name'] not in roles and user_id != user['id']:
        raise HTTPError(401, f'Not authorized.')

    crm_user = zoho_check_information(user)

    # Only updates when it has a different id or when it doesn't have id
    if user['crm_id'] != crm_user['crm_id'] or user['crm_contact_id'] != crm_user['crm_contact_id']:
        user['crm_id'] = crm_user['crm_id']
        user['crm_contact_id'] = crm_user['crm_contact_id']
    else:
        return jsonify({'user': user})

    return default_update(model_class=Users, _dict=user)


@HTTPRouter.route('api/users/role', 'PATCH')
@CheckReadOnly()
def patch_user_role(event, context):

    user_id = authorizer_get_data(event, 'user_id')
    if not user_id:
        raise HTTPError(401, f'No Valid Token')

    access_info = authorizer_get_data(event, 'access')
    access_info_json = json.loads(access_info.replace("'", '"'))

    roles = [
        'system_administrator',
        'company_administrator'
    ]

    if access_info_json['role']['name'] not in roles:
        raise HTTPError(401, f'Not authorized.')

    data = json.loads(event.get('body', None))

    return default_update(model_class=Users, _dict=data)


@HTTPRouter.route('api/users', 'DELETE')
@CheckReadOnly()
def delete_users(event, context):
    entity_id = get_request_query_parameter(param_key='id', request=event)

    return default_delete(model_class=Users, query_where={'id': entity_id})


@HTTPRouter.route('api/users/policies', 'POST')
@CheckReadOnly()
def post_user_policies(event, context):
    data = json.loads(event.get('body', None))

    return default_insert(model_or_constructor=UsersModulesPermissions, dict_=data)

@HTTPRouter.route('api/users/invite_hash', 'GET')
@CheckReadOnly()
def get_user_by_invite_hash(event, context):
    invite_hash = get_request_query_parameter(param_key='invite_hash', request=event, default_value=None)
    if not invite_hash:
        raise HTTPError(401, f'No invite hash provided.')

    user = Users.query.filter_by(invite_hash=invite_hash).first()
    if not user:
        raise HTTPError(404, f'Not found.')

    return jsonify({"id": user.id, "company_id": user.company_id})

@HTTPRouter.route('api/users/username_validation', 'POST')
@CheckReadOnly()
def validation_username(event, context):
    data = json.loads(event.get('body', None))
    username = data.get('username', None)

    user = Users.query.filter_by(email=username).first()

    return jsonify({'username': True if user else False})


@HTTPRouter.route('api/user/revoke', 'GET')
def get_users(event, context):
    username = get_request_query_parameter(
        param_key='username', request=event, default_value=None)

    result = cognito_revoke_session(username=username)

    return jsonify(result)


@HTTPRouter.route('api/users/unsubscribe_email', 'PATCH')
@CheckReadOnly()
def unsubscribe_email(event, context):
    user = json.loads(event.get('body', None))
    _user = Users.query.filter_by(
        subscription_reference=user.get("subscription_reference")).first()

    if not _user:
        raise HTTPError(404, 'User not found')
    if not _user.is_subscribed_summary:
        raise HTTPError(400, 'User is already unsubscribed')

    if not user.get('id', None):
        user.update({'id': _user.id})

    return default_update(model_class=Users, _dict=user)


@HTTPRouter.route('api/user/reset_password', 'PATCH')
@CheckReadOnly()
def admin_reset_user_password(event, context):

    access_info = authorizer_get_data(event, 'access')
    access_info_json = json.loads(access_info.replace("'", '"'))
    data = json.loads(event.get('body', None))

    roles = [
        'system_administrator',
        'company_administrator'
    ]

    if access_info_json['role']['name'] not in roles:
        raise HTTPError(401, f'Not authorized.')

    return cognito_admin_reset_user_password(data['email'])

# ENTITY CONTROLLER: Roles =============================================================================================


@HTTPRouter.route('api/roles', 'GET')
def get_roles(event, context):
    from application.functions.db.database_workspace import summary_role_permissions

    response = []
    roles = Roles.query.all()

    for role in roles:
        response.append(summary_role_permissions(role))

    return jsonify(response)

# ENTITY CONTROLLER: Groups =============================================================================================


@HTTPRouter.route('api/groups', 'GET')
def get_groups(event, context):
    return jsonify(cognito_get_all_groups()['Groups'])


# ENTITY CONTROLLER: UsersResourcesJobs ================================================================================

@HTTPRouter.route('api/users/resources/jobs', 'GET')
def get_users_resources_jobs(event, context):
    return default_list(model_class=UsersResourcesJobs)


# ENTITY CONTROLLER: Company ===========================================================================================

@HTTPRouter.route('api/user/company', 'GET')
def get_user_company(event, context):
    request_user = authorizer_get_data(event, 'email')
    user = Users.query.filter_by(email=request_user).first()

    _schema = {'relations': {
        'services': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'commodities': {'exclude': ['created_on', 'updated_on', 'company_id']},
        'sections_profile': {'include': ['id', 'name', 'tag']}
    }}

    _company_id = user.company_id if user else 0
    return default_get(model_class=Companies, query_where={'id': _company_id}, schema=_schema)


# TRIGGERS =============================================================================================================
# ======================================================================================================================
@listens_for(Users, 'after_update')
def trigger_user_update(mapper, connection, target):
    state = db.inspect(target)

    attribute_role_id_history = state.attrs.role_id.load_history().added
    attribute_is_active_history = state.attrs.is_active.load_history().added

    # Revise role change
    if attribute_role_id_history:
        cognito_revoke_session(target.email)

    # Revise user status
    if attribute_is_active_history:
        # Update in cognito
        cognito_enable_user(
            target.email) if target.is_active else cognito_disable_user(target.email)

    if target.email and target.first_name and target.last_name and target.phone:
        user_attrib = [
            {'Name': 'email', 'Value': target.email},
            {'Name': 'name', 'Value': f"{target.first_name} {target.last_name}" if target.first_name and target.last_name else None},
            {'Name': 'phone_number', 'Value': target.phone}
        ]

        user_email = Users.query.filter_by(id=target.id).first().email

        cognito_update_user_attributes(user_email, user_attrib)


@listens_for(UsersModulesPermissions, 'after_insert')
@listens_for(UsersModulesPermissions, 'after_update')
@listens_for(UsersModulesPermissions, 'after_delete')
def trigger_user_policy_update(mapper, connection, target):
    user = Users.query.filter_by(id=target.user_id).first()

    if user:
        cognito_revoke_session(username=user.email)


# EXTERNAL FUNCTIONS ===================================================================================================
# ======================================================================================================================
def _post_user_management(user):
    from application.core.aws import sqs_send_message
    from application.services.zoho_service import zoho_entity_lead
    from application.services.telegram_service import generate_message_cr_notification as telegram_generate_message_cr_notification
    from application.services.slack_service import generate_message_cr_notification as slack_generate_message_cr_notification
    from application.functions.triggers.sqs_triggers import _execute_service_compliance

    country = Countries.query.filter_by(id=user.country_id).first()
    company = Companies.query.filter_by(id=user.company_id).first()

    # STEP 1: Telegram + Slack Notification
    commodities = [
        commodity.commodity_name for commodity in company.commodities]
    telegram_message = telegram_generate_message_cr_notification(
        user_firstname=user.first_name,
        user_lastname=user.last_name,
        company_name=company.name,
        company_commodities=str(commodities).replace("'", "")
    )
    sqs_send_message(queueUrl='queue_telegram',
                     queueMessage=json.dumps({"message": telegram_message}))

    slack_message, channel = slack_generate_message_cr_notification(
        user_firstname=user.first_name,
        user_lastname=user.last_name,
        company_name=company.name,
        company_commodities=str(commodities).replace("'", "")
    )
    sqs_send_message(queueUrl='queue_slack', queueMessage=json.dumps(
        {"message": slack_message, "channel": channel}))

    # STEP 2: Check compliance > user
    sqs_send_message(queueUrl='queue_services', queueMessage=json.dumps({
        "data": {"user_first_name": user.first_name, "user_last_name": user.last_name},
        "entity": "person",
        "service": "COMPLIANCE"
    }))

    # STEP 3: ZOHO CRM Registration
    data = zoho_entity_lead(user, country, company)
    sqs_send_message(queueUrl='queue_zoho_crm', queueMessage=json.dumps({
        "user_email": user.email,
        "crm_data": data,
        "crm_operation": "INSERT_LEAD"
    }))

    # # TODO: Handler CRM error
    # if response:
    #     crm_item_id = response.get('data')[0].get('details').get('id')
    #
    #     try:
    #         cognito_update_user_attributes(user.email, [{'Name': 'custom:crm_id', 'Value': crm_item_id if crm_item_id else 'none'}])
    #     except Exception as e:
    #         print('[COGNITO SERVICE] Update attributes warning', e)
    #
    #     user.crm_id = crm_item_id
    #     user.save()
