#!/usr/bin/env python
import json
import urllib2

from uuid import uuid4

from app import app

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
	def createUser(facebookId="unset", googleId="unset"):
		userId = str(uuid4())
		DynamoDBConnection().getUserTable().put_item(
			Item={
				'userId': userId,
				'facebookId': facebookId,
				'googleId': googleId
			}
		)

		return userId

	@staticmethod
	def doesUserExist(userId):
		return True if UserModel().getUser(userId) else False

	@staticmethod
	def getUser(userId):
		res = None

		try:
			response = DynamoDBConnection().getUserTable().get_item(
				Key={
					'userId': userId
				}
			)
		except ClientError as e:
			pass
		else:
			if 'Item' in response:
				res = response['Item']

		return res


class FacebookModel(UserModel):

	@staticmethod
	def createUserWithFacebook(facebookId):
		if not FacebookModel().doesFacebookIdExist(facebookId):
			return UserModel().createUser(facebookId=facebookId)
		return False

	@staticmethod
	def getTokenValidation(token):
		url = app.config['FACEBOOK_DEBUG_URL']
		accessToken = app.config['FACEBOOK_ACCESS_TOKEN']
		res = urllib2.urlopen(url.format(input_token=token, access_token=accessToken))
		return json.loads(res.read())['data']

	@staticmethod
	def getUserByFacebookId(facebookId):
		res = False

		try:
			response = DynamoDBConnection().getUserTable().query(
				IndexName='facebookIdIndex',
				KeyConditionExpression=Key('facebookId').eq(facebookId)
			)
		except ClientError as e:
			pass
		else:
			if len(response['Items']) > 0:
				res = response['Items'][0]

		return res

	@staticmethod
	def doesFacebookIdExist(facebookId):
		user = FacebookModel().getUserByFacebookId(facebookId)
		return True if user and len(user) > 0 else False

	@staticmethod
	def registerFacebookIdToUserId(userId, facebookId):
		res = False
		if not FacebookModel().doesFacebookIdExist(facebookId):
			if UserModel().doesUserExist(userId):
				if FacebookModel().validateUserIdAndFacebookIdLink(userId, None):
					DynamoDBConnection().getUserTable().update_item(
						Key={
							'userId': userId
						},
						UpdateExpression="set facebookId = :facebookId",
						ExpressionAttributeValues={
							':facebookId': facebookId
						},
						ReturnValues="UPDATED_NEW"
					)
					res = True
		
		return res

	@staticmethod
	def unregisterFacebookIdFromUserId(userId):
		DynamoDBConnection().getUserTable().update_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set facebookId = :facebookId",
			ExpressionAttributeValues={
				':facebookId': "unset"
			},
			ReturnValues="UPDATED_NEW"
		)

	@staticmethod
	def validateUserIdAndFacebookIdLink(userId, facebookId):
		res = False
		user = UserModel().getUser(userId)
		if user and user['facebookId'] == facebookId:
			res = True

		return res

class GoogleModel(UserModel):

	@staticmethod
	def createUserWithGoogle(googleId):
		if not GoogleModel().doesGoogleIdExist(googleId):
			return UserModel().createUser(googleId=googleId)
		return False

	@staticmethod
	def getTokenValidation(token):
		pass

	@staticmethod
	def getUserByGoogleId(googleId):
		res = False

		try:
			response = DynamoDBConnection().getUserTable().query(
				IndexName='googleIdIndex',
				KeyConditionExpression=Key('googleId').eq(googleId)
			)
		except ClientError as e:
			pass
		else:
			if len(response['Items']) > 0:
				res = response['Items'][0]

		return res

	@staticmethod
	def doesGoogleIdExist(googleId):
		user = GoogleModel().getUserByGoogleId(googleId)
		return True if user and len(user) > 0 else False

	@staticmethod
	def registerGoogleIdToUserId(userId, googleId):
		res = False
		if not GoogleModel().doesGoogleIdExist(googleId):
			if UserModel().doesUserExist(userId):
				if GoogleModel().validateUserIdAndGoogleIdLink(userId, None):
					DynamoDBConnection().getUserTable().update_item(
						Key={
							'userId': userId
						},
						UpdateExpression="set googleId = :googleId",
						ExpressionAttributeValues={
							':googleId': googleId
						},
						ReturnValues="UPDATED_NEW"
					)
					res = True
		
		return res

	@staticmethod
	def unregisterGoogleIdFromUserId(userId):
		DynamoDBConnection().getUserTable().update_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set googleId = :googleId",
			ExpressionAttributeValues={
				':googleId': "unset"
			},
			ReturnValues="UPDATED_NEW"
		)

	@staticmethod
	def validateUserIdAndGoogleIdLink(userId, googleId):
		res = False
		user = UserModel().getUser(userId)
		if user and user['googleId'] == googleId:
			res = True

		return res