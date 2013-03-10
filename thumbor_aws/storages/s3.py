#coding: utf-8

import os
import calendar
from datetime import datetime, timedelta
from uuid import uuid4
import hashlib

from os.path import join

from thumbor.storages import BaseStorage
from thumbor.utils import logger

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from dateutil.parser import parse as parse_ts


class Storage(BaseStorage):

    __connection = None

    def __get_s3_connection(self):
        if self.__connection is None:
            self.__connection = S3Connection(self.context.config.AWS_ACCESS_KEY,self.context.config.AWS_SECRET_KEY)

        return self.__connection
    def __get_s3_bucket(self):
        return Bucket(
            connection=self.__get_s3_connection(),
            name=self.context.config.RESULT_STORAGE_BUCKET
        )

    def put(self, path, bytes):
        file_abspath = self.normalize_path(path)
        logger.debug("[RESULT_STORAGE] putting s3 key at %s" % (file_abspath))

        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(file_abspath)
        if not file_key:
            file_key = Key(self.context.config.RESULT_STORAGE_BUCKET,file_abspath)
        file_key.set_contents_from_string(bytes)

    def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        file_abspath = self.normalize_path(path)

        if not self.context.server.security_key:
            raise RuntimeError("STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no SECURITY_KEY specified")

        crypto_path = '%s.txt' % splitext(file_abspath)[0]

        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(crypto_path)
        if not file_key:
            file_key = Key(self.context.config.RESULT_STORAGE_BUCKET,crypto_path)

        file_key.set_contents_from_string(self.context.server.security_key)

        return file_abspath

    def put_detector_data(self, path, data):
        file_abspath = self.normalize_path(path)

        path = '%s.detectors.txt' % splitext(file_abspath)[0]
        
        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(path)
        if not file_key:
            file_key = Key(self.context.config.RESULT_STORAGE_BUCKET,path)

        file_key.set_contents_from_string(self.context.server.security_key)

        return file_abspath

    def get_crypto(self, path):
        file_abspath = self.normalize_path(path)
        crypto_file = "%s.txt" % (splitext(file_abspath)[0])

        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(crypto_path)
        if not file_key:
            return None

        return file_key.read()

    def get(self, path):

        file_abspath = self.normalize_path(path)

        logger.debug("[RESULT_STORAGE] getting from s3 key %s" % file_abspath)

        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(file_abspath)

        if not file_key or self.is_expired(file_abspath):
            logger.debug("[RESULT_STORAGE] s3 key not found at %s" % file_abspath)
            return None

        return file_key.read()

    def get_detector_data(self, path):
        file_abspath = self.normalize_path(path)
        path = '%s.detectors.txt' % splitext(file_abspath)[0]
        
        bucket = self.__get_s3_bucket()
        file_key = bucket.get_key(file_abspath)

        if not file_key or self.is_expired(file_abspath):
            return None

        return file_key.read()

    def exists(self, path):
        bucket = self.__get_s3_bucket()
        file_abspath = self.normalize_path(path)
        file_key = bucket.get_key(file_abspath)
        if not file_key:
            return False
        return True

    def normalize_path(self, path):
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        return join(self.context.config.AWS_STORAGE_ROOT_PATH.rstrip('/'), digest[:2] + '/' + digest[2:])

    def is_expired(self, key):
        if key:

            expire_in_seconds = self.context.config.get('RESULT_STORAGE_EXPIRATION_SECONDS', None)

            #Never expire
            if expire_in_seconds is None or expire_in_seconds == 0:
                return False

            
            timediff = datetime.now() - self.utc_to_local(parse_ts(key.last_modified))

            return timediff.seconds > expire_in_seconds
        else:
            #If our key is bad just say we're expired
            return True

    def utc_to_local(utc_dt):
        # get integer timestamp to avoid precision lost
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)


