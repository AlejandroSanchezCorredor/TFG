import json
from datetime import datetime, timedelta
from application.core.sql.defaults.sql_context import SQLContext
from application.functions.db.database_workspace import reduce_permissions


@SQLContext()
def update_user_crm(email=None, crm_id=False, _session_=None):
    from application.models.users_model import Users

    user = _session_.query(Users).filter_by(email=email).first()
    user.crm_id = crm_id

@SQLContext()
def update_contact_crm(email=None, crm_id=False, crm_tag=None, _session_=None):
    from application.models.contacts_model import Contacts

    contact = _session_.query(Contacts).filter_by(email=email, crm_tag=crm_tag).first()
    contact.crm_id = crm_id

@SQLContext()
def get_user_permissions(email=None, update_access=False, _session_=None):
    from application.models.users_model import Users, ConnectionLogs
    from application.models.companies_model import Companies
    from application.core.aws.sqs import sqs_send_message

    user = _session_.query(Users).filter_by(email=email).first()
    company = _session_.query(Companies).filter_by(id=user.company_id).first()

    if update_access and user:
        # Control Required: Lambdas in cognito triggers are limited to 5s of execution, so these lambdas are executed
        # multiple times on cold start.
        if not user.last_access_datetime or datetime.utcnow() > (user.last_access_datetime + timedelta(seconds=10)):
            user.last_access_datetime = datetime.utcnow()
            _session_.add(ConnectionLogs(user_id=user.id))

            _data = {
                "Last_Login": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
            }

            # If we have crm_id in the database, then we have a Zoho Lead, then update it's Last_Login in Zoho LEADS
            if user.crm_id and not user.crm_contact_id:
                sqs_send_message(queueUrl='queue_zoho_crm', queueMessage=json.dumps({
                    "user_crm_id": user.crm_id,
                    "crm_data": _data,
                    "crm_operation": "UPDATE_LEAD"
                }))
            # If we have crm_contact_id or both, crm_id and crm_contact_id, we should have a Zoho Contact, then update it's Last_Login in Zoho CONTACTS
            elif (user.crm_contact_id and not user.crm_id) or (user.crm_id and user.crm_contact_id):
                sqs_send_message(queueUrl='queue_zoho_crm', queueMessage=json.dumps({
                    "user_crm_id": user.crm_contact_id,
                    "crm_data": _data,
                    "crm_operation": "UPDATE_CONTACT"
                }))

    return user.id, user.company_id, company.name, reduce_permissions(user)
