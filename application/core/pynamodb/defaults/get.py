from application.core.http import jsonify


def default_get(model_class, hash_key, range_key=None, schema=None):
    try:
        res = model_class.get(hash_key=hash_key, range_key=range_key)
        if schema:
            res = res.from_schema(schema)
        return jsonify(res.to_dict(), statusCode=200)
    except model_class.DoesNotExist:
        return jsonify({"error": "Not Found"}, statusCode=404)
    except Exception as e:
        return jsonify({"error": str(e)}, statusCode=500)