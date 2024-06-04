import json
import logging
import math
from datetime import datetime, date
from decimal import Decimal
from numbers import Number
from urllib.parse import unquote_plus
from uuid import UUID
# from .http_request import current_request
from .http_error import HTTPError

try:
    #from sqlalchemy.ext.declarative import DeclarativeMeta
    HAS_SQL_ALCHEMY = True
except ImportError:
    HAS_SQL_ALCHEMY = False

try:
    # Numpy compatibility is only for json encoder
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

DEFAULT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS'
}

ERROR_MESSAGES = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    405: 'Method not allowed',
    500: 'Internal server error'
}

INFINITY_JSON_KEY = '@@INFINITY@@'
INFINITY_JSON_VALUE = '1e999'


def get_json_encoder(schema=None):
    def extended_encoder(x):
        if isinstance(x, datetime):
            return f'{x.isoformat()}Z'
        elif isinstance(x, date):
            return f'{x.isoformat()}'
        elif isinstance(x, UUID):
            return str(x)
        elif isinstance(x, Decimal):
            if x % 1 == 0:
                return int(x)
            else:
                return round(float(x), 12)
        elif HAS_NUMPY and isinstance(x, np.integer):
            return int(x)
        elif HAS_NUMPY and isinstance(x, np.floating):
            return float(x)
        elif HAS_NUMPY and isinstance(x, np.bool_):
            return bool(x)
        elif HAS_NUMPY and isinstance(x, np.ndarray):
            return x.tolist()
        #elif HAS_SQL_ALCHEMY and isinstance(x.__class__, DeclarativeMeta):
            #if schema is not None:
                #return x.from_schema(schema)
            #return x.to_dict()
        return x
    return extended_encoder


def jsonify(obj=None, statusCode=200, schema=None, default_fnct=None):
    def pre_parse(obj):
        """
        Replaces inf and -inf by the value @@INFINITY@@
        """
        if isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = pre_parse(v)
        elif isinstance(obj, list):
            for idx, x in enumerate(obj):
                obj[idx] = pre_parse(x)
        elif isinstance(obj, Number) and not math.isfinite(obj):
            if obj == math.inf:
                return INFINITY_JSON_KEY
            elif obj == -math.inf:
                return f'-{INFINITY_JSON_KEY}'
            return None
        return obj

    def post_parse(json_str):
        """
        Replaces "@@INFINITY@@" by 1e999
        """
        return json_str\
            .replace(f'"{INFINITY_JSON_KEY}"', INFINITY_JSON_VALUE) \
            .replace(f'"-{INFINITY_JSON_KEY}"', f'-{INFINITY_JSON_VALUE}')

    def remove_nans(json_str):
        obj = pre_parse(json.loads(json_str))
        return post_parse(json.dumps(obj))

    response = {
        'statusCode': statusCode,
        'headers': DEFAULT_HEADERS
    }
    if obj is not None:
        body = json.dumps(obj, default=default_fnct or get_json_encoder(schema))
        response['headers']['Content-Type'] = 'application/json'
        response['body'] = remove_nans(body)

    return response


def error(statusCode, message=None):
    if message:
        return jsonify({'msg': message}, statusCode)
    elif statusCode in ERROR_MESSAGES:
        return jsonify({'msg': ERROR_MESSAGES[statusCode]}, statusCode)
    return jsonify(statusCode)


def _get_and_transform(params, param_key, default_value='', unquote=True, converter=None, raise_400=True):
    if param_key not in params:
        return default_value

    value = params.get(param_key)
    if unquote:
        value = unquote_plus(value)
    if converter:
        try:
            value = converter(value)
            if converter == eval:
                value = [value] if isinstance(value, int) else list(value)
        except Exception:
            if raise_400:
                raise HTTPError(400)

    return value


def get_request_body(request, default_value={}, load_json=True, raise_400=True):
    try:
        body = request.get('body')
        if load_json:
            return json.loads(body)
        return body
    except TypeError or json.decoder.JSONDecodeError:
        if raise_400:
            raise HTTPError(400)
        return default_value


def get_request_path_parameter(param_key, request, default_value='', converter=None, raise_400=True):
    path_parameters = request.get('pathParameters', {}) or {}
    return _get_and_transform(path_parameters, param_key, default_value, True, converter, raise_400)


def get_request_query_parameter(param_key, request, default_value='', converter=None, raise_400=True):
    query_parameters = request.get('queryStringParameters', {}) or {}
    return _get_and_transform(query_parameters, param_key, default_value, True, converter, raise_400)


def _parse_boolean(string):
    d = {'true': True, 'false': False, 'none': None}
    return d.get(string, None)

