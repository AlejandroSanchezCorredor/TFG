import json
from application.core.http import HTTPRouter, get_request_query_parameter
from application.models.chats_model import Chats
from application.core.pynamodb.defaults import default_list, default_create, default_update, default_delete, default_get
from application.services.gpt_service import get_gpt_response
from application.core.http import jsonify
from application.models.properties_model import Properties
from application.models.reservations_model import Reservations

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
    id = get_request_query_parameter(param_key='pk', request=event)
    sort_key = get_request_query_parameter(param_key='sk', request=event)

    return default_delete(model_class=Chats, hash_key=id, range_key= sort_key)

@HTTPRouter.route('api/chat', 'GET')
def get_chat(event, context):
    id = get_request_query_parameter(param_key='pk', request=event)
    sort_key = get_request_query_parameter(param_key='sk', request=event)

    return default_get(model_class=Chats, hash_key=id, range_key= sort_key)

@HTTPRouter.route('api/chat', 'POST')
def post_chat(event, context):
    try:
        data = json.loads(event.get('body', ''))
        message = data.get('message')
        pk = data.get('pk')
        sk = data.get('sk')

        if not message or not pk or not sk:
            return jsonify({'error': 'Missing message, pk or sk'}, statusCode=400)
        
        pk_components = pk.split("#")
        property_pk = "#".join(pk_components[:2])
        reservation_pk = "#".join(pk_components[:3])

        property_item = default_get(model_class=Properties, hash_key=property_pk)
        reservation_item = default_get(model_class=Reservations, hash_key=reservation_pk, range_key='2024-06-07T16:54:05.315291')

        property_data = property_item.get('body', {})
        reservation_data = reservation_item.get('body', {})

        context = {
                "mensajes": message,
                "property": property_data,
                "reservation": reservation_data
            }

        gpt_answer= get_gpt_response(context)

        return jsonify({'reply': gpt_answer}, statusCode=200)
    except Exception as e:
        return jsonify({'error': str(e)}, statusCode=500)
