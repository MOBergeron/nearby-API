#!/usr/bin/env python
import json
import urllib2
import Geohash

from uuid import uuid4

from app import app

from app.connection import DynamoDBConnection

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from oauth2client import client, crypt

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonimity, latitude, longitude, message, picture=None):
		"""Creates a spotted.
		"""
		if not picture is None:
			# Save it to S3, then keep the picture link to save it in the table.
			pass

		spottedId = str(uuid4())
		geoHash = Geohash.encode(latitude, longitude, precision=7)
		DynamoDBConnection().getSpottedTable().put_item(
			Item={
				'spottedId': spottedId,
				'userId': userId,
				'geoHash': geoHash,
				'anonimity': anonimity,
				'isArchived': False,
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
		userId = str(uuid4())
		DynamoDBConnection().getUserTable().put_item(
			Item={
				'userId': userId,
				'facebookId': facebookId,
				'googleId': googleId,
				'disabled': False
			}
		)

		return userId

	@staticmethod
	def disableUser(userId):

		DynamoDBConnection().getUserTable().delete_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set disabled = :k1",
			ExpressionAttributeValues={
				':k1': True
			},
			ReturnValues='None'
		)

		DynamoDBConnection().getSpottedTable().update_item(
			Key={
				'userId': userId
			},
			UpdateExpression="set isArchived = :k1",
			ExpressionAttributeValues={
				':k1': True
			},
			ReturnValues='None'
		)


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

	@staticmethod
	def mergeUsers(userIdFrom, userIdTo):
		res = False
		if UserModel.doesUserExist(userIdFrom) and UserModel.doesUserExist(userIdTo):
			DynamoDBConnection().getSpottedTable().update_item(
				Key={
					'userId': userIdFrom
				},
				UpdateExpression="set userId = :k1",
				ExpressionAttributeValues={
					':k1': userIdTo
				},
				ReturnValues='None'
			)

			DynamoDBConnection().getUserTable().delete_item(
				Key={
					'userId': userIdFrom
				},
				ReturnValues='None'
			)
			res = True

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
			if len(response['Items']) == 1:
				res = response['Items'][0]

		return res

	@staticmethod
	def doesFacebookIdExist(facebookId):
		"""Checks if a user exists by facebookId.
		"""
		return True if FacebookModel.getUserByFacebookId(facebookId) else False

	@staticmethod
	def registerFacebookIdToUserId(userId, facebookId):
		"""Register a Facebook account to a user.
		"""
		res = False
		if not FacebookModel.doesFacebookIdExist(facebookId):
			user = UserModel.getUser(userId)
			if user and FacebookModel.validateUserIdAndFacebookIdLink(facebookId, 'unset'):
				DynamoDBConnection().getUserTable().delete_item(
					Key={
						'userId': userId
					}
				)

				res = UserModel.createUser(facebookId=facebookId, googleId=user['googleId'])
		
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
		CLIENT_ID = app.config['GOOGLE_CLIENT_ID']
		
		tokenInfo = None
		try:
			tokenInfo = client.verify_id_token(token, CLIENT_ID)

			if tokenInfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
				raise crypt.AppIdentityError("Wrong issuer.")

		except crypt.AppIdentityError as e:
			print(e)
			tokenInfo = False
		
		return tokenInfo

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
			print(e)
		else:
			if len(response['Items']) == 1:
				res = response['Items'][0]

		return res

	@staticmethod
	def doesGoogleIdExist(googleId):
		"""Checks if a user exists by googleId.
		"""
		return True if GoogleModel.getUserByGoogleId(googleId) else False

	@staticmethod
	def registerGoogleIdToUserId(userId, googleId):
		"""Register a Google account to a user.
		"""
		res = False
		if not GoogleModel.doesGoogleIdExist(googleId):
			user = UserModel.getUser(userId)
			if user and GoogleModel.validateUserIdAndGoogleIdLink(userId, 'unset'):
				DynamoDBConnection().getUserTable().delete_item(
					Key={
						'userId': userId
					}
				)

				res = UserModel.createUser(facebookId=user['facebookId'], googleId=googleId)
		
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