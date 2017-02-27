#!/usr/bin/env python
import re
from datetime import datetime
from bson import ObjectId
from json import JSONEncoder
	
uuidRegex = re.compile('^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}\Z')

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

def validateObjectId(objId):
	return ObjectId.is_valid(objId)

def validateUUID(uuid):
	if uuidRegex.match(str(uuid)):
		return True
	return False