from application.core.http import jsonify


def default_create(model_or_constructor, dict_, post_create_fn=None, custom_parser=None, schema=None):
    res = model_or_constructor(**dict_)
    res.save()
    if post_create_fn:
        post_create_fn(res)
    if not schema:
        schema = model_or_constructor.base_schema() or {'exclude': []}
    return jsonify(custom_parser and custom_parser(res) or res, statusCode=201, schema=schema)
