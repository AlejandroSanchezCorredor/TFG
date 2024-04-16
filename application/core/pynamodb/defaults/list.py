from application.core.http import jsonify, current_request
import json

QS_PAGE = '_page'
QS_PAGE_SIZE = '_page_size'
QS_FIELDS = '_fields'
QS_ORDER_BY = '_order_by'


def _get_pagination(query_string):
    page = query_string.get(QS_PAGE, 'null')
    try:
        page = json.loads(page or 'null')
    except ValueError:
        raise AttributeError('_page needs to be a valid DynamoDB-encoded dictionary with the key(s)')

    page_size = query_string.get(QS_PAGE_SIZE, 10)
    try:
        page_size = int(page_size)
    except ValueError:
        raise AttributeError('_page_size needs to be integer')
    if page_size < 0:
        raise AttributeError('_page_size needs to be >= 0')

    return page, page_size


def _get_custom_schema(query_string):
    fields = query_string.get(QS_FIELDS, '')
    if not fields:
        return None
    fields_list = fields.split(',')
    return {
        'include': fields_list
    }


def _get_order_by(query_string):
    sort_by = query_string.get(QS_ORDER_BY, '')
    return (sort_by.split('-', maxsplit=1)[-1], True if sort_by.startswith('-') else False) if sort_by else None


def default_list(model_class, hash_key=None, range_key_condition=None, filter_condition=None,
                 schema=None, jsonify_response=True):
    if hash_key:
        return default_list_query(model_class, hash_key=hash_key, range_key_condition=range_key_condition,
                                  filter_condition=filter_condition, schema=schema, jsonify_response=jsonify_response)
    return default_list_scan(model_class, schema=schema, filter_condition=filter_condition,
                             jsonify_response=jsonify_response)


def default_list_scan(model_class, schema=None, filter_condition=None, jsonify_response=True):
    query_string = current_request.event['queryStringParameters'] or {}
    page, page_size = _get_pagination(query_string)
    schema = _get_custom_schema(
        query_string) or schema or model_class.base_schema()
    # TODO: implement
    # filter_condition = None

    if page_size:
        scan = model_class.scan(
            filter_condition=filter_condition,
            limit=page_size,
            last_evaluated_key=page
        )
    else:
        scan = model_class.scan(
            filter_condition=filter_condition
        )

    # Se iteran antes para obtener el last_evaluated_key
    if schema is not None:
        items = [item.from_schema(schema) for item in scan]
    else:
        items = [item.to_dict() for item in scan]

    res = {
        "nextElement": scan.last_evaluated_key,
        "pageSize": page_size,
        "items": items
    }

    if jsonify_response:
        return jsonify(res, schema=schema)
    return res


def default_list_query(model_class, hash_key, range_key_condition=None, filter_condition=None,
                       schema=None, jsonify_response=True):
    query_string = current_request.event['queryStringParameters'] or {}
    page, page_size = _get_pagination(query_string)
    schema = _get_custom_schema(
        query_string) or schema or model_class.base_schema()
    # TODO: implement
    # filter_condition = None

    query = model_class.query(
        hash_key=hash_key,
        range_key_condition=range_key_condition,
        filter_condition=filter_condition,
        limit=page_size,
        last_evaluated_key=page
    )

    # Se iteran antes para obtener el last_evaluated_key
    if schema is not None:
        items = [item.from_schema(schema) for item in query]
    else:
        items = [item.to_dict() for item in query]

    res = {
        "nextElement": query.last_evaluated_key,
        "pageSize": page_size,
        "items": items
    }

    if jsonify_response:
        return jsonify(res, schema=schema)
    return res, schema


def default_list_global_order(model_class, order_attr=None, reverse=False, filter_condition=None):
    # def insort(iterable, item, key=lambda x: x):
    #     low = 0
    #     high = len(iterable)
    #     compare = lambda x, y: x > y if reverse else lambda x, y: x < y
    #
    #     while low < high:
    #         mid = (low + high) >> 1
    #         if compare(key(iterable[mid]), key(item)):
    #             low = mid + 1
    #             print(item.surname)
    #         else:
    #             high = mid
    #
    #     iterable[low:low] = [item]

    query_string = current_request.event['queryStringParameters'] or {}
    page, page_size = _get_pagination(query_string)
    page = 0 if page is None else page
    schema = _get_custom_schema(query_string) or {'exclude': []}

    order_by, reverse = _get_order_by(query_string) or (order_attr, reverse)
    all_items = []
    key = lambda x: getattr(x, order_by)
    for register in model_class.scan(filter_condition=filter_condition):
        all_items.append(register)
        # insort(all_items, register, key=key)

    all_items = sorted(all_items, key=key, reverse=reverse)

    if schema is not None:
        items = [item.from_schema(schema) for item in all_items[page * page_size:(page * page_size) + page_size]]
    else:
        items = [item.to_dict() for item in all_items[page * page_size:(page * page_size) + page_size]]

    res = {
        "page": page,
        "page_size": page_size,
        "total": len(all_items),
        "items": items
    }

    return jsonify(res)
