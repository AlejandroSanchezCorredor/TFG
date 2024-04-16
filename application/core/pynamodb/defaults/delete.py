from application.core.http import jsonify


def default_delete(model_class, hash_key, range_key=None):
    res = model_class.get(hash_key=hash_key, range_key=range_key)
    res.delete()

    return jsonify(statusCode=204)
