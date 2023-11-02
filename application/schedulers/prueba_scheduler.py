from application.core.scheduler.scheduler_router import SchedulerTasker
from application.core.http.http_router import HTTPRouter

@HTTPRouter.route_request('api/test_scheduler', 'GET')
def prueba(event, context):
    return None