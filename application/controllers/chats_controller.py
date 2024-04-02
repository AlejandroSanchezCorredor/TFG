import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.core.sql.defaults import default_list, default_get, default_create, default_delete, default_update
from application.models.chats_model import Chats



# ENTITY CONTROLLER: Chats ========================================================================================

@HTTPRouter.route('api/chats', 'GET')
def get_chats(event, context):
    _schema = {'exclude': ['created_on', 'updated_on']}
    return default_list(model_class=Chats, schema=_schema)

@HTTPRouter.route('api/chats', 'POST')
def post_chats(event, context):
    data = json.loads(event.get('body', None))

    return default_create(model_or_constructor=Chats, dict_=data)


@HTTPRouter.route('api/chats', 'PATCH')
def patch_chats(event, context):
    data = json.loads(event.get('body', None))

    return default_update(model_class=Chats, _dict=data)


@HTTPRouter.route('api/chats', 'DELETE')
def delete_chats(event, context):
    id = get_request_query_parameter(param_key='id', request=event)

    return default_delete(model_class=Chats, query_where={'id': id})