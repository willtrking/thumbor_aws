#coding: utf-8

import calendar
from datetime import datetime, timedelta
import hashlib
import os

from thumbor.result_storages import BaseStorage
from thumbor.utils import logger

from boto.s3.bucket import Bucket
from boto.s3.key import Key
from dateutil.parser import parse as parse_ts

import thumbor_aws.connection

class Storage(BaseStorage):

    @property
    def is_auto_webp(self):
        return self.context.config.AUTO_WEBP and self.context.request.accepts_webp

    def __init__(self, context):
        BaseStorage.__init__(self, context)
        self.storage = self.__get_s3_bucket()

    def __get_s3_bucket(self):
        return Bucket(
            connection=thumbor_aws.connection.get_connection(self.context),
            name=self.context.config.RESULT_STORAGE_BUCKET
        )

    def put(self, bytes):
        file_abspath = self.normalize_path(self.context.request.url)
        file_key=Key(self.storage)
        file_key.key = file_abspath

        file_key.set_contents_from_string(bytes,
            encrypt_key = self.context.config.get('S3_STORAGE_SSE', default=False),
            reduced_redundancy = self.context.config.get('S3_STORAGE_RRS', default=False)
        )

    def get(self):
        file_abspath = self.normalize_path(self.context.request.url)
        file_key = self.storage.get_key(file_abspath)

        if not file_key or self.is_expired(file_key):
            logger.debug("[RESULT_STORAGE] s3 key not found at %s" % file_abspath)
            return None

        return file_key.read()

    def normalize_path(self, path):
        root_path = self.context.config.get('RESULT_STORAGE_AWS_STORAGE_ROOT_PATH', default='thumbor/result_storage/')
        path_segments = [path]
        if self.is_auto_webp:
            path_segments.append("webp")
        digest = hashlib.sha1(".".join(path_segments).encode('utf-8')).hexdigest()
        return os.path.join(root_path, digest)

    def is_expired(self, key):
        if key:
            timediff = datetime.now() - self.utc_to_local(parse_ts(key.last_modified))
            return timediff.seconds > self.context.config.STORAGE_EXPIRATION_SECONDS
        else:
            #If our key is bad just say we're expired
            return True

    def last_updated(self):
        path = self.context.request.url
        file_abspath = self.normalize_path(path)
        file_key = self.storage.get_key(file_abspath)

        if not file_key or self.is_expired(file_key):
            logger.debug("[RESULT_STORAGE] s3 key not found at %s" % file_abspath)
            return None

        return self.utc_to_local(parse_ts(file_key.last_modified))

    def utc_to_local(self,utc_dt):
        # get integer timestamp to avoid precision lost
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)
