# coding: utf-8

from boto.s3.connection import S3Connection

connection = None

def get_connection(context):
    conn = connection
    if conn is None:
        if context.config.get('AWS_ROLE_BASED_CONNECTION', default=False):
            conn = S3Connection()
        else:
            conn = S3Connection(
                context.config.get('AWS_ACCESS_KEY'),
                context.config.get('AWS_SECRET_KEY')
            )

    return conn
