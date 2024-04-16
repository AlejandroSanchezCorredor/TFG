from application.core.http import jsonify


def default_get(model_class, hash_key, range_key=None, schema=None):
    res = model_class.get(hash_key=hash_key, range_key=range_key)
    if schema:
        res = res.from_schema(schema)

    return jsonify(res)
