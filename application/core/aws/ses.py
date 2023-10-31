import boto3
from application.core.configuration_loader import get_configuration


def send_email(message, recipient, subject="CHECKIT Notification", sender=None, monitor=False, charset="UTF-8"):
    configuration = get_configuration()

    ses_client = boto3.client('ses')
    response = ses_client.send_email(
        Destination={
            'ToAddresses': [recipient],
            'BccAddresses': [configuration.SES_EMAIL_MONITOR] if monitor else []
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': charset,
                    'Data': message,
                },
            },
            'Subject': {
                'Charset': charset,
                'Data': subject,
            },
        },
        Source=f'CHECKIT Platform <{sender or configuration.SES_EMAIL_SENDER}>',
    )

    return response
