import json
from application.core.http import HTTPRouter, get_request_query_parameter, jsonify
from application.core.sql.defaults import default_list, default_get, default_create, default_delete, default_update
from application.models.products_model import Products



# ENTITY CONTROLLER: Categories ========================================================================================

@HTTPRouter.route('api/products', 'GET')
def get_products(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}
    return default_list(model_class=Products, schema=_schema)

@HTTPRouter.route('api/products', 'POST')
def post_products(event, context):
    data = json.loads(event.get('body', None))

    return default_create(model_or_constructor=Products, dict_=data)


@HTTPRouter.route('api/products', 'PATCH')
def patch_products(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Products, _dict=data)


@HTTPRouter.route('api/products', 'DELETE')
def delete_products(event, context):
    id = get_request_query_parameter(param_key='id', request=event)

    return default_delete(model_class=Products, query_where={'id': id})