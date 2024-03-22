import json
from application.core.http import HTTPRouter, get_request_query_parameter, jsonify
from application.core.sql.defaults import default_list, default_get, default_create, default_delete, default_update
from application.models.resources_model import ResourcesCategories



# ENTITY CONTROLLER: Categories ========================================================================================

@HTTPRouter.route('api/myusers', 'GET')
def get_categories(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}
    return default_list(model_class=ResourcesCategories, schema=_schema)

@HTTPRouter.route('api/myusers', 'POST')
def post_categories(event, context):
    data = json.loads(event.get('body', None)) 

    return default_create(model_or_constructor=ResourcesCategories, dict_=data)


@HTTPRouter.route('api/myusers', 'PATCH')
def patch_categories(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=ResourcesCategories, _dict=data)


@HTTPRouter.route('api/myusers', 'DELETE')
def delete_categories(event, context):
    id = get_request_query_parameter(param_key='id', request=event)

    return default_delete(model_class=ResourcesCategories, query_where={'id': id})

