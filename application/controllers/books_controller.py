import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.models.books_model import Books
from application.core.pynamodb.defaults import default_list, default_create, default_update, default_delete



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
    id = get_request_query_parameter(param_key='pk', request=event)
    sort_key = get_request_query_parameter(param_key='sk', request=event)

    return default_delete(model_class=Books, hash_key=id, range_key= sort_key)

