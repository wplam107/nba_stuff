import ndjson
from google.cloud import storage
from configparser import ConfigParser
from os import system

def to_json(data, file):
    """
    Write data to newline delimited JSON file
    """

    with open(file, 'w') as f:
        ndjson.dump(data, f)

    print(f'{file} written.')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def set_configs():
    """
    Sets configs for project
    """

    config = ConfigParser()
    config.read('./private/config.ini')
    BUCKET = config.get('gcp', 'BUCKET')

    return BUCKET