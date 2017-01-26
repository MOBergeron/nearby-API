#!/usr/bin/env python
from app.connection import DynamoDBConnection

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonimity, latitude, longitude, message, picture=None):
		if not picture is None:
			# Save it to S3, then keep the picture link to save it in the table.
			pass

		response = DynamoDBConnection().getSpottedTable().put_item(
			Item={
				'spottedId': "yolo",
				'userId': userId,
				'anonimity': anonimity,
				'latitude': latitude,
				'longitude': longitude,
				# Add picture link here
				'message': message
			}
		)

		return response

	@staticmethod
	def getSpottedBySpottedId(spottedId):
		res = {}
		try:
			response = DynamoDBConnection().getSpottedTable().get_item(
				Key={
					'spottedId': spottedId
				}
			)
		except ClientError as e:
			res['error'] = response['Error']['Message']
		else:
			res['item'] = response['Item']

		return res

	@staticmethod
	def __getSpotteds(userId, latitude, longitude, radius, locationOnly):
		res = {}
		try:
			response = DynamoDBConnection().getSpottedTable().get_item(
				Key={
					'userId': spottedId
				}
			)
		except ClientError as e:
			res['error'] = response['Error']['Message']
		else:
			res['item'] = response['Item']

		return res

	@staticmethod
	def getSpotteds(latitude, longitude, radius, locationOnly):
		return self.__getSpotteds(userId=None, latitude=latitude, longitude=longitude, radius=radius, locationOnly=locationOnly)

	@staticmethod
	def getSpottedsByUserId(userId):
		return self.__getSpotteds(userId=userId, latitude=None, longitude=None, radius=None, locationOnly=None)

class UserModel(object):
	pass		