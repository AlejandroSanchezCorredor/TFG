import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.models.properties_model import Properties
from application.core.pynamodb.defaults import default_list, default_create, default_update, default_delete
import os



# ENTITY CONTROLLER: Properties ========================================================================================

@HTTPRouter.route('api/properties', 'GET')
def get_properties(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}

    return default_list(model_class=Properties, schema=_schema)

@HTTPRouter.route('api/properties', 'POST')
def post_properties(event, context):
    data = json.loads(event.get('body', None))
    return default_create(model_or_constructor=Properties, dict_=data)


@HTTPRouter.route('api/properties', 'PATCH')
def patch_properties(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Properties, _dict=data)


@HTTPRouter.route('api/properties', 'DELETE')
def delete_properties(event, context):
    id = get_request_query_parameter(param_key='pk', request=event)

    return default_delete(model_class=Properties, hash_key=id)