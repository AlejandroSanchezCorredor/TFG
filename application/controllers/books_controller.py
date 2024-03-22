import json
from application.core.http import HTTPRouter, get_request_query_parameter, jsonify
from application.core.sql.defaults import default_list, default_get, default_create, default_delete, default_update
from application.models.books_model import Books



# ENTITY CONTROLLER: Books ========================================================================================

@HTTPRouter.route('api/books', 'GET')
def get_books(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}
    return default_list(model_class=Books, schema=_schema)

@HTTPRouter.route('api/books', 'POST')
def post_books(event, context):
    data = json.loads(event.get('body', None)) 

    return default_create(model_or_constructor=Books, dict_=data)


@HTTPRouter.route('api/books', 'PATCH')
def patch_books(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Books, _dict=data)


@HTTPRouter.route('api/books', 'DELETE')
def delete_books(event, context):
    id = get_request_query_parameter(param_key='id', request=event)

    return default_delete(model_class=Books, query_where={'id': id})

