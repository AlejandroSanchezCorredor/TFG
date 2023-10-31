from application.core.http import jsonify


def default_get(model_class, query_where={}, custom_parser=None, schema=None):
    query = model_class.smart_query(
        filters=query_where,
        schema=schema
    )

    res = query.one()
    return jsonify(custom_parser and custom_parser(res) or res, schema=schema)
