import os
import re
import logging
from application.core.aws.ssm import get_parameter

class BaseConfiguration(object):
    APP_SERVICE = os.environ.get('AWS_SERVICE', 'TFG_Booking-application')
    APP_BOT = 'bot@system'

    # AWS CONFIGURATION
    AWS_STAGE = os.getenv('AWS_STAGE', None)
    AWS_REGION = os.environ.get('AWS_REGION', None)

    # > AWS SERVICE: COGNITO
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID', None)
    COGNITO_USER_POOL_CLIENT_ID = os.getenv('COGNITO_USER_POOL_CLIENT_ID', None)

    # > AWS SERVICE: SES
    SES_EMAIL_SENDER = os.getenv('SES_EMAIL_SENDER_ADDRESS', None)

    # DATABASE CONFIGURATION
    DATABASE_TYPE = 'mysql+pymysql'
    DATABASE_USER = os.getenv('RDS_MASTER_USER', None)
    DATABASE_PASSWORD = os.getenv('RDS_MASTER_PASSWORD', None)
    DATABASE_URI = os.getenv('RDS_AURORA_ENDPOINT', None)
    DATABASE_PORT = os.getenv('RDS_AURORA_PORT', None)
    DATABASE_DB = os.getenv('RDS_AURORA_DB', None)


    # ENVIRONMENT CONFIGURATION
    DEBUG_SQL = False
    LOG_LEVEL = logging.WARNING

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