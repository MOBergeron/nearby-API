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
		"""Creates a spotted.
		"""
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
		"""Gets a spotted by spottedId.
		"""
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				KeyConditionExpression=Key("spottedId").eq(spottedId)
			)
		except ClientError as e:
			pass
		else:
			if len(response['Items']) == 1:
				res = response['Items'][0]

		return res

	@staticmethod
	def getSpotteds(latitude, longitude, radius, locationOnly):
		"""Gets a list of spotteds by using the latitude, longitude and radius.
		locationOnly returns only get the location of the returned spotteds if true.
		"""
		return []

	@staticmethod
	def getMySpotteds(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				IndexName='userIdIndex',
				KeyConditionExpression="userId = :k1",
				ExpressionAttributeValues={
					':k1' : userId
				}
			)
		except ClientError as e:
			print(e)
		else:
			res = response['Items']

		return res

	@staticmethod
	def getSpottedsByUserId(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				IndexName='userIdIndex',
				KeyConditionExpression="userId = :k1",
				FilterExpression="anonimity = :f1",
				ExpressionAttributeValues={
					":k1" : userId,
					":f1" : False
				}
			)
		except ClientError as e:
			print(e)
		else:
			res = response['Items']

		return res

class UserModel(object):

	@staticmethod
	def createUser(facebookId='unset', googleId='unset'):
		"""THIS METHOD SHOULDN'T BE USED ELSEWHERE THAN IN FacebookModel AND GoogleModel.
		Creates a user with either facebookId or googleId.
		"""
		userId = False
		if facebookId == 'unset' or googleId == 'unset' and not facebookId == googleId:
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
		"""Checks if a user exists by userId.
		"""
		return True if UserModel.getUser(userId) else False

	@staticmethod
	def getUser(userId):
		"""Gets a user by userId.
		"""
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
		"""Creates a user related to a facebookId.
		"""
		if not FacebookModel.doesFacebookIdExist(facebookId):
			return UserModel.createUser(facebookId=facebookId)
		return False

	@staticmethod
	def getTokenValidation(token):
		"""Calls Facebook to receive a validation of a Facebook user token.
		"""
		url = app.config['FACEBOOK_DEBUG_URL']
		accessToken = app.config['FACEBOOK_ACCESS_TOKEN']
		res = urllib2.urlopen(url.format(input_token=token, access_token=accessToken))
		return json.loads(res.read())['data']

	@staticmethod
	def getUserByFacebookId(facebookId):
		"""Gets a user by facebookId.
		"""
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
		"""Checks if a user exists by facebookId.
		"""
		user = FacebookModel.getUserByFacebookId(facebookId)
		return True if user and len(user) > 0 else False

	@staticmethod
	def registerFacebookIdToUserId(userId, facebookId):
		"""Register a Facebook account to a user.
		"""
		res = False
		if not FacebookModel.doesFacebookIdExist(facebookId):
			if UserModel.doesUserExist(userId):
				if FacebookModel.validateUserIdAndFacebookIdLink(userId, None):
					DynamoDBConnection().getUserTable().update_item(
						Key={
							'userId': userId
						},
						UpdateExpression="set facebookId = :facebookId",
						ExpressionAttributeValues={
							':facebookId': facebookId
						},
						ReturnValues='None'
					)
					res = True
		
		return res

	@staticmethod
	def unregisterFacebookIdFromUserId(userId):
		"""Unregister a Facebook account from a user.
		"""
		DynamoDBConnection().getUserTable().update_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set facebookId = :facebookId",
			ExpressionAttributeValues={
				':facebookId': 'unset'
			},
			ReturnValues='None'
		)

	@staticmethod
	def validateUserIdAndFacebookIdLink(userId, facebookId):
		"""Validate the link between a user and a Facebook account.
		"""
		res = False
		user = UserModel.getUser(userId)
		if user and user['facebookId'] == facebookId:
			res = True

		return res

class GoogleModel(UserModel):

	@staticmethod
	def createUserWithGoogle(googleId):
		"""Creates a user related to a googleId.
		"""
		if not GoogleModel.doesGoogleIdExist(googleId):
			return UserModel.createUser(googleId=googleId)
		return False

	@staticmethod
	def getTokenValidation(token):
		"""Calls Google to receive a validation of a Google user token.
		"""
		pass

	@staticmethod
	def getUserByGoogleId(googleId):
		"""Gets a user by googleId.
		"""
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
		"""Checks if a user exists by googleId.
		"""
		user = GoogleModel.getUserByGoogleId(googleId)
		return True if user and len(user) > 0 else False

	@staticmethod
	def registerGoogleIdToUserId(userId, googleId):
		"""Register a Google account to a user.
		"""
		res = False
		if not GoogleModel.doesGoogleIdExist(googleId):
			if UserModel.doesUserExist(userId):
				if GoogleModel.validateUserIdAndGoogleIdLink(userId, None):
					DynamoDBConnection().getUserTable().update_item(
						Key={
							'userId': userId
						},
						UpdateExpression="set googleId = :googleId",
						ExpressionAttributeValues={
							':googleId': googleId
						},
						ReturnValues='None'
					)
					res = True
		
		return res

	@staticmethod
	def unregisterGoogleIdFromUserId(userId):
		"""Unregister a Google account from a user.
		"""
		DynamoDBConnection().getUserTable().update_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set googleId = :googleId",
			ExpressionAttributeValues={
				':googleId': 'unset'
			},
			ReturnValues='None'
		)

	@staticmethod
	def validateUserIdAndGoogleIdLink(userId, googleId):
		"""Validate the link between a user and a Google account.
		"""
		res = False
		user = UserModel.getUser(userId)
		if user and user['googleId'] == googleId:
			res = True

		return res