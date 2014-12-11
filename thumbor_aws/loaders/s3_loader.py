# coding: utf-8

from boto.s3.bucket import Bucket
from boto.s3.key import Key
import urllib2

import thumbor_aws.connection

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


def load(context, url, callback):
    url = urllib2.unquote(url)
    if context.config.S3_LOADER_BUCKET:
        bucket = context.config.S3_LOADER_BUCKET
    else:
        bucket, url = _get_bucket(url)
        if not _validate_bucket(context, bucket):
            return callback(None)

    bucket_loader = Bucket(
        connection=thumbor_aws.connection.get_connection(context),
        name=bucket
    )

    file_key = bucket_loader.get_key(url)
    if not file_key:
        return callback(None)

    return callback(file_key.read())
