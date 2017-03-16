#!/usr/bin/env python
import os
import boto
import cStringIO

from PIL import Image
from uuid import uuid4
from bson import ObjectId
from json import JSONEncoder
from boto.s3.key import Key
from datetime import datetime

# Validate if the object ID is a valid ObjectId.
def validateObjectId(objId):
	return ObjectId.is_valid(objId)

# Create thumbnail image from image.
def createThumbnail(self, image):
	im = Image.open(image)
	im.thumbnail((1440,1440), Image.ANTIALIAS)
	thumbnailIm = cStringIO.StringIO()
	im.save(thumbnailIm, 'JPEG')
	return thumbnailIm.getvalue()

# http://stackoverflow.com/q/6760685
class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class CustomJSONEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		elif isinstance(o, datetime):
			return o.isoformat()
		else:
			return o

class S3Connection():
	__metaclass__ = Singleton

	__REGION_HOST = "s3.ca-central-1.amazonaws.com"
	__EXTENSION = "JPEG"

	def __init__(self):
		os.environ['S3_USE_SIGV4'] = 'True'
		connection = boto.connect_s3(host=self.__REGION_HOST)
		self.__bucket = connection.get_bucket("spottednearby")

	def saveFile(self, file):
		uuid = uuid4()
		filename = "{filename}{extension}".format(filename=uuid, extension=self.__EXTENSION)
		k = Key(self.__bucket)
		k.key = filename
		k.set_contents_from_string(file)
		k.make_public()

		return "https://{region}/{bucketName}/{keyName}".format(region=self.__REGION_HOST,bucketName=self.__bucket.name, keyName=filename)
