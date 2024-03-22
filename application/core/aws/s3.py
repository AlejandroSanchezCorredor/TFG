import boto3
from application.core.configuration_loader import get_configuration


def s3_get_object(key, bucketname=None):
    """Get object from S3 Bucket

    :param key: string
    :param bucketname: string
    :return: the object (bytes)
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    return s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()


def s3_get_object_tagging(key, bucketname=None):
    """Get object tags from S3 Bucket

    :param key: string
    :param bucketname: string
    :return: the object (bytes)
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    return s3_client.get_object_tagging(Bucket=bucket, Key=key)


def s3_get_object_head(key, bucketname=None):
    """Get object metadata from S3 Bucket

    :param key: string
    :param bucketname: string
    :return: the object (bytes)
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    return s3_client.head_object(Bucket=bucket, Key=key)


def s3_save_file(key, content, bucketname=None, contenttype=None):
    """Save object to S3 Bucket

    :param key: string
    :param content: the content of the object
    :param bucketname: string
    :return: absolute path of S3 where the object has been stored
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    s3_client.put_object(
        Body=content,
        Bucket=bucket,
        Key=key,
        ContentType=contenttype)

    path = f'{bucket}/{key}'
    return path


def s3_delete_file(key, bucketname=None):
    """Delete object from S3 Bucket

    :param key: string
    :param bucketname: string
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    s3_client.delete_object(Bucket=bucket, Key=key)


def s3_delete_directoy(directory, bucketname=None):
    """Delete all objects inside folder from S3 Bucket

    :param directory: string
    :param bucketname: string
    """

    configuration = get_configuration()

    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucketname or configuration.S3_BUCKET_STORAGE)

    bucket.objects.filter(Prefix=f"{directory}/").delete()


def s3_copy_file(source_key, destination_key, source_bucket=None, destination_bucket=None, tagging=None):
    """Delete object from S3 Bucket

    :param source_key: string
    :param destination_key: string
    :param source_bucket: string
    :param destination_bucket: string
    :param tagging: string
    """

    configuration = get_configuration()
    s3_client = boto3.client('s3')

    source_bucket = source_bucket or configuration.S3_BUCKET_STORAGE
    destination_bucket = destination_bucket or configuration.S3_BUCKET_STORAGE

    s3_client.copy_object(
        Bucket=destination_bucket,
        Key=destination_key,
        Tagging=tagging,
        TaggingDirective='REPLACE',
        CopySource={'Bucket': source_bucket, 'Key': source_key}
    )


def s3_get_signed_url(key, bucketname=None, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param key: string
    :param bucketname: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: presigned URL as string
    """

    configuration = get_configuration()

    s3_client = boto3.client('s3')
    bucket = bucketname or configuration.S3_BUCKET_STORAGE

    signed_url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        },
        ExpiresIn=expiration
    )

    return signed_url