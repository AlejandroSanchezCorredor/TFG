import logging
from .log_types import RequestType
from .log_webhook import webhook_send
from ..configuration_loader import get_configuration

LOGGING_NUM = 25    # In between INFO(20) and WARNING(30)
LOGGING_NAME = "SLS-LOG"


class LogRequest:
    pass


class LogHandler(object):
    DEFAULT_LOGGING_FORMAT = '%(levelname)s: %(message)s'

    @staticmethod
    def setup_logging(format=DEFAULT_LOGGING_FORMAT, level=logging.WARNING):
        logging.addLevelName(LOGGING_NUM, LOGGING_NAME)
        logger = logging.getLogger()
        if logger.hasHandlers():
            logger.setLevel(level)
            logger.handlers[0].setFormatter(logging.Formatter(format))
        else:
            logging.basicConfig(format=format, level=level)

    @staticmethod
    def _init_log_level():
        try:
            config = get_configuration()
            log_level = getattr(config, 'LOG_LEVEL', logging.WARNING)
        except:
            log_level = logging.WARNING

        LogHandler.setup_logging(level=log_level)

    @staticmethod
    def _get_request_type(event):
        if event.get('source', None) == 'keep-warm':
            return RequestType.KEEP_WARM
        elif event.get('type', None) == 'TOKEN':
            return RequestType.AUTHORIZER_TOKEN
        elif event.get('resource', None) and event.get('httpMethod', None) and event.get('headers', None):
            return RequestType.API_GATEWAY
        elif event.get('Records', None) and type(event['Records']) is list and 'eventSource' in event['Records'][0]:
            first_event_source = event['Records'][0]['eventSource']
            if first_event_source == 'aws:kinesis':
                return RequestType.AWS_EVENT_KINESIS
            elif first_event_source == 'aws:dynamodb':
                return RequestType.AWS_EVENT_DYNAMODB
            elif first_event_source == 'aws:s3':
                return RequestType.AWS_EVENT_S3
            elif first_event_source == 'aws:sns':
                return RequestType.AWS_EVENT_SNS
            elif first_event_source == 'aws:sqs':
                return RequestType.AWS_EVENT_SQS
            return RequestType.AWS_EVENT_UNKNOWN
        return RequestType.UNKNOWN

    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            try:
                request = LogRequest()
                LogHandler._init_log_level()
                request.event = args[0]
                request.context = args[1]
                request.type = LogHandler._get_request_type(args[0])
                return orig_func(*args, **kwargs)
            except Exception as e:
                webhook_send(request, e)
                raise e
        return wrapper
