# coding: utf-8

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key

connection = None

def _get_bucket(url):
    """
    Returns a tuple containing bucket name and bucket path.
    url: A string of the format /bucket.name/file/path/in/bucket
    """

    url_by_piece = url.lstrip("/").split("/")
    bucket_name = url_by_piece[0]
    bucket_path = "/".join(url_by_piece[1:])
    return bucket_name, bucket_path

def _validate_bucket(context,bucket):
    if not context.config.S3_ALLOWED_BUCKETS:
        return True

    for allowed in context.config.S3_ALLOWED_BUCKETS:
        #s3 is case sensitive
        if allowed == bucket:
            return True

    return False


def _establish_connection(context_config):
    conn = connection
    if conn is None:
        # Store connection not bucket
        conn = S3Connection(
            context_config.AWS_ACCESS_KEY,
            context_config.AWS_SECRET_KEY
        )

    return conn

def load(context, url, callback):
    if context.config.S3_LOADER_BUCKET:
        bucket = context.config.S3_LOADER_BUCKET
    else:
        bucket, url = _get_bucket(url)
        if not _validate_bucket(context, bucket):
            return callback(None)

    conn = _establish_connection(context.config)

    bucket_loader = Bucket(
        connection=conn,
        name=bucket
    )

    file_key = bucket_loader.get_key(url)
    if not file_key:
        return callback(None)

    return callback(file_key.read())
