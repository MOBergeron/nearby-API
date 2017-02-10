#!/usr/bin/env python
import json
import math
import decimal

from geohash import encore_uint64
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

# http://stackoverflow.com/a/2189827
def intLength(n):
	if n > 0:
		digits = int(math.log10(n))+1
	elif n == 0:
		digits = 1
	else:
		digits = int(math.log10(-n))+2

	return digits

def generateHashKey(geohash, length):
	geohashLength = intLength(geohash)
	if geohashLength > length:
		return geohash/int(math.pow(10, geohashLength-length))
	elif geohashLength < length:
		return geohash*int(math.pow(10, length-geohashLength))
	else:
		return geohash

def generateGeohash(lat, lng):
	return encore_uint64(lat, lng)

def generateBoundaries(geohash, length):
	geohashLength = intLength(geohash)
	if geohashLength < length:
		return (geohash*int(math.pow(10, length-geohashLength)), ((geohash+1)*int(math.pow(10, length-geohashLength)))-1)
	elif geohashLength > length:
		return (geohash/int(math.pow(10, geohashLength-length)), geohash/int(math.pow(10, geohashLength-length)))
	else:
		return (geohash, geohash)