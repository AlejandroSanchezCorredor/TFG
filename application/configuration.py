import os
import re
from application.core.aws.ssm import get_parameter

class BaseConfiguration(object):
    APP_SERVICE = os.environ.get('AWS_SERVICE', 'TFG_Booking-application')
    APP_BOT = 'bot@system'

    # AWS CONFIGURATION
    AWS_STAGE = os.getenv('AWS_STAGE', None)
    AWS_REGION = os.environ.get('AWS_REGION', None)

    # > AWS SERVICE: SES
    SES_EMAIL_SENDER = os.getenv('SES_EMAIL_SENDER_ADDRESS', None)

    # BOOKING EXTRANET CONFIGURATION
    BOOKING_EXTRANET_USER = os.getenv('BOOKING_EXTRANER_USER', None)
    BOOKING_EXTRANET_PASSWORD = os.getenv('BOOKING_EXTRANER_PASSWORD', None)

    def __getattribute__(self, name):
        item = object.__getattribute__(self, name)
        if item is None:
            # If not get value, check in SSM + Cache
            item = get_parameter(name.lower())
            object.__setattr__(self, name, item)

        return item

    @classmethod
    def get(cls, key):
        item = getattr(cls, key)
        if type(item) is str:
            item = cls.format(item)
        return item

    @classmethod
    def format(cls, _str):
        replace_keys = re.findall('{(.*?)}', _str)
        replace_items = {k: cls.get(k) for k in replace_keys}
        return _str.format(**replace_items)


configuration = BaseConfiguration()