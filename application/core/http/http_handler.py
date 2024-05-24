import logging
import traceback
from .http_request import current_request
from .http_functions import error, HTTPError
from ..log.log_types import RequestType
from ..configuration_loader import get_configuration


LOGGING_NUM = 25    # In between INFO(20) and WARNING(30)
LOGGING_NAME = "SLS-LOG"


class HTTPHandler(object):
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

        HTTPHandler.setup_logging(level=log_level)

    @staticmethod
    def _get_request_type(event):
        if event.get('source', None) == 'keep-warm':
            return RequestType.KEEP_WARM
        elif event.get('type', None) == 'TOKEN':
            return RequestType.AUTHORIZER_TOKEN
        elif event.get('resource', None) and event.get('httpMethod', None) and event.get('headers', None):
            return RequestType.API_GATEWAY
        elif event.get('Records', None) and type(event['Records']) is list and 'EventSource' in event['Records'][0]:
            first_event_source = event['Records'][0]['EventSource']
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

    @staticmethod
    def _handle_exception(exception):
        logging.error('Event: {}'.format(current_request.event))
        logging.error(traceback.format_exc())
        if current_request.type == RequestType.API_GATEWAY:
            return error(exception.statusCode, exception.message) if type(exception) == HTTPError else error(500)
        elif current_request.type == RequestType.AUTHORIZER_TOKEN:
            raise Exception('Unauthorized')
        raise exception

    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            try:
                HTTPHandler._init_log_level() # Inicializamos el logging
                current_request.event = args[0]
                current_request.context = args[1]
                current_request.type = HTTPHandler._get_request_type(args[0]) # Identificamos el tipo de request
                return orig_func(*args, **kwargs) # Ejecutamos la función original
            except Exception as e:
                return HTTPHandler._handle_exception(e)
            finally:
                current_request.clear()
        return wrapper
