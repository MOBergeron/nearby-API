#!/usr/bin/env python
import os
import boto

from uuid import uuid4
from boto.s3.key import Key

from app.utils import Singleton

class S3Connection():
	__metaclass__ = Singleton

	__REGION_HOST = "s3.ca-central-1.amazonaws.com"
	__EXTENSION = "JPEG"

	def __init__(self):
		os.environ['S3_USE_SIGV4'] = 'True'
		connection = boto.connect_s3(host=self.__REGION_HOST)
		self.__bucket = connection.get_bucket("spottednearby")

	def saveFile(self, file):
		#_, extension = os.path.splitext(file.filename)
		uuid = uuid4()
		filename = "{filename}{extension}".format(filename=uuid, extension=self.__EXTENSION)
		k = Key(self.__bucket)
		k.key = filename
		k.set_contents_from_string(file)
		k.make_public()

		return "https://{region}/{bucketName}/{keyName}".format(region=self.__REGION_HOST,bucketName=self.__bucket.name, keyName=filename)
