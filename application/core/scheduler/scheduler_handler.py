import logging
import traceback
# from .scheduler_error import error
from .scheduler_task import current_task
from ..log.log_types import RequestType
from ..log.log_webhook import webhook_send
from ..configuration_loader import get_configuration


LOGGING_NUM = 25    # In between INFO(20) and WARNING(30)
LOGGING_NAME = "SLS-LOG"


class SchedulerHandler(object):
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

        SchedulerHandler.setup_logging(level=log_level)

    @staticmethod
    def _handle_exception(exception):
        logging.error('Event: {}'.format(current_task.event))
        logging.error(traceback.format_exc())
        raise exception

    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            try:
                SchedulerHandler._init_log_level()
                current_task.event = args[0]
                current_task.context = args[1]
                current_task.type = 'SCHEDULER'
                return orig_func(*args, **kwargs)
            except Exception as e:
                webhook_send(current_task, e)
                return SchedulerHandler._handle_exception(e)
            finally:
                current_task.clear()
        return wrapper
