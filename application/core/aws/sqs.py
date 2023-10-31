import boto3
from application.core.configuration_loader import get_configuration


def _get_queue_by_alias(alias):
    configuration = get_configuration()

    QUEUE_TASKS = {
        'queue_email': configuration.SQS_EMAIL_NOTIFICATION,
        'queue_mass_emails': configuration.SQS_MASS_EMAILS,
        'queue_zoho_crm': configuration.SQS_ZOHO_CRM_NOTIFICATION,
        'queue_telegram': configuration.SQS_TELEGRAM_NOTIFICATION,
        'queue_slack': configuration.SQS_SLACK_NOTIFICATION,
        'queue_all_users': configuration.SQS_ALL_USERS_NOTIFICATION,
        'queue_services': configuration.SQS_SERVICES_NOTIFICATION,
        'queue_blockchain': configuration.SQS_SERVICES_BLOCKCHAIN_HEDERA
    }

    return QUEUE_TASKS.get(alias, None)


def sqs_get_queue_url(queueName):
    """Retrieves url queue from queue name

    :param queueName: string
    :return: dict {'QueueUrl': 'string'}
    """

    sqs_client = boto3.client('sqs')

    return sqs_client.get_queue_url(QueueName=queueName)


def sqs_get_queue_attributes(queueUrl):
    """Retrieves ottributes from the specified queue.

    :param queueUrl: string
    :return: object queue
    """

    sqs_client = boto3.client('sqs')

    return sqs_client.get_queue_attributes(
        AttributeNames=['All'],
        QueueUrl=queueUrl
    )


def sqs_send_message(queueUrl, queueMessage, queueMessageGroupId=None):
    """Retrieves one or more messages (up to 10), from the specified queue.

    :param queueUrl: string
    :return: list sqs messages
    """
    sqs_client = boto3.client('sqs')

    _queueUrl = _get_queue_by_alias(queueUrl) or queueUrl

    send_message_params = {"MessageBody": queueMessage, "QueueUrl": _queueUrl}

    if queueMessageGroupId:
        send_message_params.update({"MessageGroupId": queueMessageGroupId})

    return sqs_client.send_message(**send_message_params)


def sqs_send_message_batch(queueUrl, entriesList, queueMessageGroupId=None):
    """Sends one or more messages (up to 10), to the specified queue.

    :param queueUrl: string
    :return: list sqs messages
    """
    sqs_client = boto3.client('sqs')

    _queueUrl = _get_queue_by_alias(queueUrl) or queueUrl

    send_message_params = {"Entries": entriesList, "QueueUrl": _queueUrl}

    if queueMessageGroupId:
        send_message_params.update({"MessageGroupId": queueMessageGroupId})

    return sqs_client.send_message_batch(**send_message_params)


def sqs_receive_queue_messages(queueUrl):
    """Retrieves one or more messages (up to 10), from the specified queue.

    :param queueUrl: string
    :return: list sqs messages
    """

    sqs_client = boto3.client('sqs')

    return sqs_client.receive_message(
        AttributeNames=['All'],
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10,
        QueueUrl=queueUrl
    )