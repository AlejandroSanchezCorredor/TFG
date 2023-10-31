import boto3


def get_parameter(key, default=None):
    """Get param from SSM Store

    :param key: string
    :return: the value key (string)
    """

    try:
        ssm_client = boto3.client('ssm')
        param = ssm_client.get_parameter(Name=key)

        if param:
            return param.get('Parameter').get('Value', None)

    except Exception as e:
        print(f"[AWS: SSM] GET_PARAMETER > Exception: {e} {key}")

    return default