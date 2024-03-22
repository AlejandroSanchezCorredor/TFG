# import logging
from pywebpush import webpush, WebPushException
from application.core.configuration_loader import get_configuration


def send_push_notification(subscription, data):
    """Send webpush protocol notification

    :param subscription: string
    :param data: object
    :return: response send push (boolean)
    """

    configuration = get_configuration()

    try:
        response = webpush(
            data=data,
            subscription_info=subscription,
            vapid_private_key=configuration.WEBPUSH_PRIVATE_VAPID,
            vapid_claims={"sub": f"mailto:{configuration.SES_EMAIL_MONITOR}"},
            timeout=5.00
        )

        print("__WEBPUSH_RESPONSE__: ", response)

        return True

    except WebPushException as wpException:
        # logging.warning('[WARNING] Webpush > Push notification could not be delivered', repr(wpException))
        print('[WARNING] Webpush > Push notification could not be delivered', repr(wpException))

        # Mozilla returns additional information
        if wpException.response and wpException.response.json():
            _extra = wpException.response.json()
            # logging.warning(' >> [PUSH LOG]', _extra)
            print(' >> [PUSH LOG]', _extra)

        return False
