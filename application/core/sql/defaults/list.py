import re
from application.core.sql import And, Or
from application.core.http import jsonify, current_request
from sqlalchemy_mixins.smartquery import RELATION_SPLITTER, OPERATOR_SPLITTER

QS_PAGE = '_page'
QS_PAGE_SIZE = '_page_size'
QS_FIELDS = '_fields'
QS_FILTER = '_filter_'
QS_FILTER_TYPE = '_operator'
QS_ORDER_BY = '_order_by'

CONDITIONS_RELATION_SPLITTER = '.'


def _get_pagination(query_string):
    page = query_string.get(QS_PAGE, 0)
    try:
        page = int(page)
    except ValueError:
        raise AttributeError('_page needs to be integer')
    if page < 0:
        raise AttributeError('_page needs to be >= 0')

    page_size = query_string.get(QS_PAGE_SIZE, 20)
    try:
        page_size = int(page_size)
    except ValueError:
        raise AttributeError('_page_size needs to be integer')
    if page_size < 0:
        raise AttributeError('_page_size needs to be >= 0')

    return page, page_size


def _get_query_string_filters(query_string):
    def _get_filter_condition(filter_key, filter_value):
        if re.search(regex, filter_key):  # filter includes operation
            field, operator = filter_key.rsplit(OPERATOR_SPLITTER, 1)
            _value = filter_value.split(',')
        else:  # filter does not include operation
            field = filter_key
            operator = 'ilike'
            _value = '%{}%'.format(filter_value)
        _key = '{}{}{}' \
            .format(field, OPERATOR_SPLITTER, operator) \
            .replace(CONDITIONS_RELATION_SPLITTER, RELATION_SPLITTER)
        return _key, _value

    filters = []
    regex = '\w{}\w+$'.format(OPERATOR_SPLITTER)
    for key, value in query_string.items():
        if key.startswith(QS_FILTER):
            keys = key[len(QS_FILTER):]
            conditions = [_get_filter_condition(k, value) for k in keys.split(',')]
            if len(conditions) == 1:
                _filter = {conditions[0][0]: conditions[0][1]}
            else:
                _filter = Or(*[{val[0]: val[1]} for val in conditions])
            filters.append(_filter)

    filter_type = query_string.get(QS_FILTER_TYPE, 'and')
    operation = Or if filter_type == 'or' else And
    return operation(*filters)


def _get_order_by(query_string):
    sort_by = query_string.get(QS_ORDER_BY, '')
    sort_by = sort_by.replace(CONDITIONS_RELATION_SPLITTER, RELATION_SPLITTER)
    return sort_by and sort_by.split(',') or []


def _get_custom_schema(query_string):
    fields = query_string.get(QS_FIELDS, '')
    if not fields:
        return None
    fields_list = fields.split(',')
    return {
        'include': fields_list
    }


def default_list(model_class, query_where={}, custom_parser=None, schema=None):
    query_string = current_request.event['queryStringParameters'] or {}
    page, page_size = _get_pagination(query_string)
    sort_attrs = _get_order_by(query_string)
    filters = _get_query_string_filters(query_string)
    schema = _get_custom_schema(query_string) or schema or model_class.base_schema()   # TODO: Merge base_schema
    query_where = And(query_where, filters)

    query = model_class.smart_query(
        filters=query_where,
        sort_attrs=sort_attrs,
        schema=schema
    )

    items = query.limit(page_size).offset(page * page_size).all() if page_size else query.all()
    total = query.order_by(None).count() if page_size else len(items)
    res = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items
    }

    return jsonify(custom_parser and custom_parser(res) or res, schema=schema)
