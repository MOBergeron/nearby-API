#!/usr/bin/env python
import json
import decimal

from uuid import UUID

# http://stackoverflow.com/q/6760685
class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

# http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.Python.03.html
class DecimalEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, decimal.Decimal):
			if o % 1 > 0:
				return float(o)
			else:
				return int(o)
		return super(DecimalEncoder, self).default(o)

# https://gist.github.com/ShawnMilo/7777304
def validateUuid(uuid):
	try:
		uuid = uuid.replace('-','')
		val = UUID(uuid, version=4)
	except ValueError:
		return False

	return val.hex == uuid