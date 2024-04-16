from application.core.http import jsonify


def default_create(model_or_constructor, dict_, schema=None, post_fn=None):
    res = model_or_constructor(**dict_)
    res.save()

    if post_fn:
        post_fn(res)

    return jsonify(res.to_dict(), statusCode=201, schema=schema)
