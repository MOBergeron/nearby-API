#!/usr/bin/env python
import json
import math
import urllib2

from decimal import Decimal
from uuid import uuid4

from app.connection import DynamoDBConnection
from app.utils import generateBoundaries, generateGeohash, generateHashKey, intLength

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
		geohash = generateGeohash(latitude, longitude)

		hashKey = generateHashKey(geohash, 6)
		DynamoDBConnection().getSpottedTable().put_item(
			Item={
				'hashKey': hashKey,
				'spottedId': spottedId,
				'userId': userId,
				'geohash': geohash,
				'geoJson': {
					'type':'Point',
					'coordinates': [
						Decimal(latitude), 
						Decimal(longitude)
					]
				},
				'anonimity': anonimity,
				'isArchived': False,
				# Add save date
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
				IndexName='SpottedBySpottedId',
				KeyConditionExpression="spottedId = :k1",
				ExpressionAttributeValues={
					':k1' : spottedId
				}
			)
		except ClientError as e:
			pass
		else:
			if len(response['Items']) == 1:
				res = response['Items'][0]

		return res

	@staticmethod
	def getSpotteds(minLat, minLong, maxLat, maxLong, locationOnly):
		"""Gets a list of spotteds by using the latitude, longitude and radius.
		locationOnly returns only get the location of the returned spotteds if true.
		"""
		res = False
		geohashNW = generateGeohash(minLat, minLong)
		geohashSW = generateGeohash(maxLat,minLong)
		geohashNE = generateGeohash(minLat,maxLong)
		geohashSE = generateGeohash(maxLat, maxLong)

		geohash = 0

		for i in range(1,20):
			if int(geohashNW/math.pow(10,i)) == int(geohashSW/math.pow(10,i)) \
				and int(geohashNW/math.pow(10,i)) == int(geohashNE/math.pow(10,i)) \
				and int(geohashNW/math.pow(10,i)) == int(geohashSE/math.pow(10,i)):
				geohash = int(geohashNW/math.pow(10,i))
				break

		lower, higher = generateBoundaries(geohash, intLength(geohashNW))
		hashKey = generateHashKey(geohash, 6)

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				IndexName='SpottedByGeohash',
				KeyConditionExpression="hashKey = :k1 AND geohash BETWEEN :k2 AND :k3",
				ExpressionAttributeValues={
					':k1' : hashKey,
					':k2' : lower,
					':k3' : higher
				}
			)
		except ClientError as e:
			print(e)
		else:
			res = response['Items']

		return res

	@staticmethod
	def getMySpotteds(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		res = False

		try:
			response = DynamoDBConnection().getSpottedTable().query(
				IndexName='SpottedByUserId',
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
				IndexName='SpottedByUserId',
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
	def createUser(facebookToken='unset', googleToken='unset'):
		"""THIS METHOD SHOULDN'T BE USED ELSEWHERE THAN IN FacebookModel AND GoogleModel.
		Creates a user with either facebookToken or googleToken.
		"""
		userId = str(uuid4())
		facebookId = 'unset'
		googleId = 'unset'
		fullName = 'unset'
		profilPictureURL = 'unset'

		if not facebookToken == 'unset':
			facebookId = facebookToken['user_id']
			url = "https://graph.facebook.com/{facebookId}?fields=name,picture&access_token={accessToken}"
			res = urllib2.urlopen(url.format(facebookId=facebookId,accessToken=facebookToken['token']))
			data = json.loads(res.read())
			profilPictureURL = data['picture']['data']['url']
			fullName = data['name']
		
		if not googleToken == 'unset':
			googleId = googleToken['sub']
			profilPictureURL = googleToken['picture']
			fullName = googleToken['name']

		DynamoDBConnection().getUserTable().put_item(
			Item={
				'userId': userId,
				'facebookId': facebookId,
				'googleId': googleId,
				'fullName': fullName,
				'profilPictureURL': profilPictureURL,
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
	def createUserWithFacebook(facebookToken):
		"""Creates a user related to a facebookToken.
		"""
		if not FacebookModel.doesFacebookIdExist(facebookToken['user_id']):
			return UserModel.createUser(facebookToken=facebookToken)
		return False

	@staticmethod
	def getTokenValidation(accessToken, token):
		"""Calls Facebook to receive a validation of a Facebook user token.
		"""
		url = "https://graph.facebook.com/debug_token?input_token={input_token}&access_token={accessToken}"
		res = urllib2.urlopen(url.format(input_token=token, accessToken=accessToken))
		data = json.loads(res.read())['data']
		data['token'] = token
		return data

	@staticmethod
	def getUserByFacebookId(facebookId):
		"""Gets a user by facebookId.
		"""
		res = False

		try:
			response = DynamoDBConnection().getUserTable().query(
				IndexName='facebookIdIndex',
				KeyConditionExpression="facebookId = :k1",
				ExpressionAttributeValues={
					':k1': facebookId
				}
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
	def createUserWithGoogle(googleToken):
		"""Creates a user related to a googleToken.
		"""
		if not GoogleModel.doesGoogleIdExist(googleToken['sub']):
			return UserModel.createUser(googleToken=googleToken)
		return False

	@staticmethod
	def getTokenValidation(clientId, token):
		"""Calls Google to receive a validation of a Google user token.
		"""
		tokenInfo = None
		try:
			tokenInfo = client.verify_id_token(token, clientId)

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
				KeyConditionExpression="googleId = :k1",
				ExpressionAttributeValues={
					':k1': googleId
				}
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
