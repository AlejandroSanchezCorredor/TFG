import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.models.reservations_model import Reservations
from application.core.pynamodb.defaults import default_list, default_create, default_update, default_delete



# ENTITY CONTROLLER: Reservations ========================================================================================

@HTTPRouter.route('api/reservations', 'GET')
def get_reservations(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}
    
    return default_list(model_class=Reservations, schema=_schema)

@HTTPRouter.route('api/reservations', 'POST')
def post_reservations(event, context):
    data = json.loads(event.get('body', None)) 

    return default_create(model_or_constructor=Reservations, dict_=data)


@HTTPRouter.route('api/reservations', 'PATCH')
def patch_reservations(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Reservations, _dict=data)


@HTTPRouter.route('api/reservations', 'DELETE')
def delete_reservations(event, context):
    id = get_request_query_parameter(param_key='pk', request=event)
    sort_key = get_request_query_parameter(param_key='sk', request=event)

    return default_delete(model_class=Reservations, hash_key=id, range_key= sort_key)

'''
from application.core.scheduler import SchedulerTasker
import datetime

@SchedulerTasker.task('activa')
def miprueba(event, context):
    print("Prueba Scheduler")
    today = datetime.datetime.now()
    print("Hora actual:", today.strftime("%H:%M:%S"))
'''

