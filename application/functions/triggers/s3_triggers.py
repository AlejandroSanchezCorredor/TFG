from application.core.aws.s3 import s3_get_object_tagging, s3_copy_file, s3_delete_file, s3_get_object_head
from urllib.parse import unquote_plus


TAG_STATIC_KEY = '_static_path'


def upload_file_trigger(event, context):
    """this trigger is invoked when a new object is created in the s3 bucket

    :param event: dict
    :param context: AWS Lambda context
    :return: event (dict)
    """

    # Get file uploaded of event info
    s3_source_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    s3_source_bucket = unquote_plus(event['Records'][0]['s3']['bucket']['name'])

    # Get tags object of event
    s3_tags = s3_get_object_tagging(key=s3_source_key, bucketname=s3_source_bucket).get("TagSet")

    # Search specific tag for static_path
    static_path = next((tag.get("Value") for tag in s3_tags if tag.get("Key") == TAG_STATIC_KEY), None)

    # Move file to static location
    if static_path:
        s3_destination_bucket, s3_destination_key = static_path.split("/", 1)

        print(f'COPYNG...\n'
              f'> [ORIGIN] {s3_source_bucket}/{s3_source_key}\n'
              f'> [DESTINATION] {s3_destination_bucket}/{s3_destination_key}')

        # Copy file (source > destination)
        # > Replace tag for source origin
        s3_copy_file(
            source_key=s3_source_key,
            destination_key=s3_destination_key,
            source_bucket=s3_source_bucket,
            tagging=f'_temporal_source_path={s3_source_bucket}/{s3_source_key}'
        )

        # Remove file (source)
        s3_delete_file(bucketname=s3_source_bucket, key=s3_source_key)

    return event