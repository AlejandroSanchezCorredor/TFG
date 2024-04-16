from application.core.http import jsonify


def default_update(model_class, _dict, hash_key=None, range_key=None, schema=None):

    # Other option
    #res = model_class.get(hash_key=hash_key, range_key=range_key)
    #for (key, value) in _dict.items():
        #setattr(model_class, key, value)
    #res.save()

    # Other option
    res = model_class(**_dict)
    res.save()

    return jsonify(res.to_dict(), schema=schema)
