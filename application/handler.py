from application.core.http import HTTPHandler
from application.core.scheduler import SchedulerHandler, SchedulerTasker
#from application.core.sql.defaults.sql_layer import SQLLayer
from application.controllers import *
from application.functions.scraping.get_books import *
from application.functions.scraping.get_flats import *
from application.functions.scraping.get_chats import *


@HTTPHandler()
# @SQLLayer()
def api(event, context):
    return HTTPRouter.route_request(event, context)


@SchedulerHandler()
# @SQLLayer()
def scheduler(event, context):
    return SchedulerTasker.task_request(event, context)
    

