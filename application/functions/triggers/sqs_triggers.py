import json
from application.core.log.log_handler import LogHandler
from application.core.sql.defaults import default_update
from application.core.sql.defaults.sql_layer import SQLLayer


@LogHandler()
@SQLLayer()
def queue_email_notification_trigger(event, context):
    """this trigger is invoked when records are created in the email queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.core.aws.ses import send_email

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _subject = _record.get('subject')
        _message = _record.get('message')
        _recipient = _record.get('recipient')
        _monitor = _record.get('monitor', False)

        send_email(message=_message, subject=_subject, recipient=_recipient, monitor=_monitor)

@LogHandler()
@SQLLayer()
def queue_mass_emails_trigger(event, context):
    """this trigger is invoked when records are created in the mass emails email queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from time import sleep
    from application.models.mass_emails_model import MassEmails
    from application.core.aws.ses import send_email

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _subject = _record.get('subject')
        _message = _record.get('message')
        _recipient = _record.get('recipient')
        _monitor = _record.get('monitor', False)
        _mass_email_id = _record.get('mass_email_id', None)

        _filters = [MassEmails.id==_mass_email_id, MassEmails.success==True]
        response = None
        if not MassEmails.session.query(MassEmails).filter(*_filters).first():
            response = send_email(message=_message, subject=_subject, recipient=_recipient, monitor=_monitor)

        if _mass_email_id and response and response['MessageId']:
            _mass_email = {'id': _mass_email_id, 'success': True}
            default_update(model_class=MassEmails, _dict=_mass_email)
            # Manual commit to avoid rollback on error
            MassEmails.session.commit()
            # Delay to avoid 14 emails per second limit
            sleep(0.2)

@LogHandler()
def queue_zoho_crm_notification_trigger(event, context):
    """this trigger is invoked when records are created in the email queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.core.aws import cognito_update_user_attributes
    from application.services.zoho_service import zoho_crm_insert_lead, zoho_crm_update_lead, zoho_crm_update_contact
    from application.functions.db.database_controller import update_user_crm
    from application.functions.db.database_controller import update_contact_crm


    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _user_email = _record.get('user_email', None)
        _user_crm_id = _record.get('user_crm_id', None)
        _crm_data = _record.get('crm_data', None)
        _crm_operation = _record.get('crm_operation', None)
        _crm_tag = _record.get('crm_tag', None)

        if _crm_operation == 'INSERT_LEAD':
            response = zoho_crm_insert_lead(_crm_data)

            user_crm_id = response.get('data')[0].get('details').get('id')

            # STEP 1: Update cognito user info
            cognito_update_user_attributes(_user_email, [{'Name': 'custom:crm_id', 'Value': user_crm_id}])

            # STEP 2: Update database user info
            update_user_crm(email=_user_email, crm_id=user_crm_id)
        elif _crm_operation == 'UPDATE_LEAD':
            zoho_crm_update_lead(_user_crm_id, _crm_data)
        elif _crm_operation == 'INSERT_CONTACT':
            response = zoho_crm_insert_lead(_crm_data)

            user_crm_id = response.get('data')[0].get('details').get('id')
            
            update_contact_crm(email=_user_email, crm_id=user_crm_id, crm_tag=_crm_tag)
        elif _crm_operation == 'UPDATE_CONTACT':
            zoho_crm_update_contact(_user_crm_id, _crm_data)
        else:
            raise Exception('CRM_OPERATION Not found')


@LogHandler()
def queue_telegram_notification_trigger(event, context):
    """this trigger is invoked when records are created in the telegram queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.services.telegram_service import send_telegram

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _message = _record.get('message')

        send_telegram(payload=_message)


@LogHandler()
def queue_slack_notification_trigger(event, context):
    """this trigger is invoked when records are created in the slack queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.services.slack_service import send_slack

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _message = _record.get('message')
        _channel = _record.get('channel')

        send_slack(payload=_message, channel=_channel)


@LogHandler()
def queue_all_users_notification_trigger(event, context):
    """this trigger is invoked when records are created in the all_users queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    from application.services.notification_service import send_notification

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _target = _record.get('target')
        _payload = _record.get('payload')
        _protocols = _record.get('protocols')

        send_notification(
            target=_target,
            payload=_payload,
            protocols=_protocols
        )


@LogHandler()
def queue_services_trigger(event, context):
    """this trigger is invoked when records are created in the services queue

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    messages = event.get('Records', [])

    for message in messages:
        _record = json.loads(message.get('body'))

        _service = _record.get('service', None)

        if _service == 'COMPLIANCE':
            _execute_service_compliance(_record)


# SERVICE FUNCTIONS ====================================================================================================
# ======================================================================================================================
def _execute_service_compliance(_record):
    from application.services.comply_advantage_service import comply_advantage_entity_search, comply_advantage_search
    from application.services.telegram_service import send_telegram, generate_message_user_compliance_notification as telegram_generate_message_user_compliance_notification, \
        generate_message_company_compliance_notification as telegram_generate_message_company_compliance_notification
    from application.services.slack_service import send_slack, generate_message_user_compliance_notification as slack_generate_message_user_compliance_notification, \
        generate_message_company_compliance_notification as slack_generate_message_company_compliance_notification

    _data = _record.get('data', None)
    _entity = _record.get('entity', None)

    if _data and _entity:
        _user_first_name = _data.get("user_first_name", None)
        _user_last_name = _data.get("user_last_name", None)
        _company_name = _data.get("company_name", None)

        search_options = comply_advantage_entity_search(
            user_first_name=_user_first_name,
            user_last_name=_user_last_name,
            company_name=_company_name,
            entity_search=_entity
        )

        result = comply_advantage_search(search_options)

        if _entity == 'person':
            telegram_message = telegram_generate_message_user_compliance_notification(
                user_firstname=_user_first_name,
                user_lastname=_user_last_name,
                hits=result.get('content').get('data').get('total_matches'),
                share_url=result.get('content').get('data').get('share_url'),
            )
            send_telegram(payload=telegram_message)

            slack_message, channel = slack_generate_message_user_compliance_notification(
                user_firstname=_user_first_name,
                user_lastname=_user_last_name,
                hits=result.get('content').get('data').get('total_matches'),
                share_url=result.get('content').get('data').get('share_url'),
            )
            send_slack(payload=slack_message, channel=channel)

        if _entity == 'company':
            telegram_message = telegram_generate_message_company_compliance_notification(
                company_name=_company_name,
                hits=result.get('content').get('data').get('total_matches'),
                share_url=result.get('content').get('data').get('share_url'),
            )
            send_telegram(payload=telegram_message)
            slack_message, channel = slack_generate_message_company_compliance_notification(
                company_name=_company_name,
                hits=result.get('content').get('data').get('total_matches'),
                share_url=result.get('content').get('data').get('share_url'),
            )
            send_slack(payload=slack_message, channel=channel)


