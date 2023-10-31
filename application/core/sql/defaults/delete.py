from application.core.http import jsonify


def default_delete(model_class, query_where, post_delete_fn=None, custom_parser=None):
    res = model_class.where(query_where).one()
    res.delete()
    if post_delete_fn:
        post_delete_fn(res)
    return custom_parser and jsonify(custom_parser(res)) or jsonify(statusCode=204)
