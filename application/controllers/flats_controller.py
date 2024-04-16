import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.models.flats_model import Flats
from application.core.pynamodb.defaults import default_list, default_create, default_update, default_delete



# ENTITY CONTROLLER: Flats ========================================================================================

@HTTPRouter.route('api/flats', 'GET')
def get_flats(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}

    return default_list(model_class=Flats, schema=_schema)

@HTTPRouter.route('api/flats', 'POST')
def post_flats(event, context):
    data = json.loads(event.get('body', None))
    print("Data")
    print(data)
    return default_create(model_or_constructor=Flats, dict_=data)


@HTTPRouter.route('api/flats', 'PATCH')
def patch_flats(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Flats, _dict=data)


@HTTPRouter.route('api/flats', 'DELETE')
def delete_flats(event, context):
    id = get_request_query_parameter(param_key='pk', request=event)

    return default_delete(model_class=Flats, hash_key=id)