import json
from sqlalchemy.event import listens_for
from application.core.configuration_loader import get_configuration
from application.core.http import HTTPRouter, get_request_query_parameter, jsonify, HTTPError
from application.core.sql.defaults import default_list, default_get, default_create, default_update, default_insert, default_delete

from application.models.users_model import Users


# ENTITY CONTROLLER: Users =============================================================================================

@HTTPRouter.route('api/users', 'POST')
def post_user(event, context):
    body = json.loads(event.get('body', None))
    return default_create(model_or_constructor=Users, dict_=body)


@HTTPRouter.route('api/users', 'GET')
def get_users(event, context):
    return default_list(model_class=Users)



@HTTPRouter.route('api/user', 'GET')
def get_user(event, context):
    id = get_request_query_parameter('id', event, default_value=None)
    if id:
        _filter = {'id': id}
    return default_get(model_class=Users, query_where=_filter)