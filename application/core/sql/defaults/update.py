from application.core.http import jsonify


def default_update(model_class, _dict, query_where=None, post_update_fn=None, custom_parser=None, schema=None):

    # Default by unique ID
    if not query_where:
        if _dict.get('id', None):
            query_where = {'id': _dict.get('id')}
            del _dict['id']

    res = model_class.where(query_where).one()

    res.update(**_dict)
    if post_update_fn:
        post_update_fn(res)
    return jsonify(custom_parser and custom_parser(res) or res, schema=schema)
