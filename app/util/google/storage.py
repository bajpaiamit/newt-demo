from google.cloud import storage
import re
import json

st_client = storage.Client()


def list_blobs(bucket, prefix=None):
    bucket = st_client.get_bucket(bucket)
    if prefix:
        blobs = bucket.list_blobs(prefix=prefix)
    else:
        blobs = bucket.list_blobs()

    return blobs


def copy_blob(blob, bucket_name, destination_path):
    destination_bucket = st_client.bucket(bucket_name)
    blob_copy = destination_bucket.copy_blob(blob, destination_bucket, destination_path)
    return blob_copy


def get_config(gcs_path, conf_key):
    matches = re.match("gs://(.*?)/(.*)", gcs_path)

    try:
        if matches:
            bucket_name, blob_name = matches.groups()
            bucket = st_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            message = json.loads(blob.download_as_text())

            return message[conf_key]

        else:
            print(f"No matches found for path {gcs_path}")
            return None

    except Exception as e:
        raise e


def get_bucket(output_bucket):
    return st_client.get_bucket(output_bucket)


def get_blob(bucket, blob_name):
    return bucket.get_blob(blob_name)
