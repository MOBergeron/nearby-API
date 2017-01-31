#!/usr/bin/env python
import json
import urllib2

from uuid import uuid4

from app.connection import DynamoDBConnection

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonimity, latitude, longitude, message, picture=None):
		if not picture is None:
			# Save it to S3, then keep the picture link to save it in the table.
			pass

		spottedId = str(uuid4())
		DynamoDBConnection().getSpottedTable().put_item(
			Item={
				'spottedId': spottedId,
				'userId': userId,
				'anonimity': anonimity,
				'latitude': latitude,
				'longitude': longitude,
				# Add picture link here
				'message': message
			}
		)

		return spottedId

	@staticmethod
	def getSpottedBySpottedId(spottedId):
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				KeyConditionExpression=Key("spottedId").eq(spottedId)
			)
		except ClientError as e:
			pass
		else:
			res = response['Items'][0]

		return res

	@staticmethod
	def __getSpotteds(userId, latitude, longitude, radius, locationOnly):
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				IndexName='userIdIndex',
				KeyConditionExpression=Key("userId").eq(userId)
			)
		except ClientError as e:
			pass
		else:
			res = response['Items']

		return res

	@staticmethod
	def getSpotteds(latitude, longitude, radius, locationOnly):
		return SpottedModel.__getSpotteds(userId=None, latitude=latitude, longitude=longitude, radius=radius, locationOnly=locationOnly)

	@staticmethod
	def getSpottedsByUserId(userId):
		return SpottedModel.__getSpotteds(userId=userId, latitude=None, longitude=None, radius=None, locationOnly=None)

class UserModel(object):
	
	@staticmethod
	def validateFacebookToken(url, token, accessToken):
		res = urllib2.urlopen(url.format(input_token=token, access_token=accessToken))
		return json.loads(res.read())['data']['is_valid']
