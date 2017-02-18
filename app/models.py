#!/usr/bin/env python
import json
import urllib2
import datetime

from bson import ObjectId
from oauth2client import client, crypt

from app import mongo
from app.s3connection import S3Connection

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonymity, latitude, longitude, message, picture=None):
		"""Creates a spotted.
		"""
		pictureURL = None
		if not picture is None:
			pictureURL = S3Connection().saveFile(picture)

		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return mongo.db.spotteds.insert_one(
			{
				'userId': userId,
				'anonymity': anonymity,
				'archived': False,
				'location': {
					'type':'Point',
					'coordinates': [
						float(latitude), 
						float(longitude)
					]
				},
				'creationDate': datetime.datetime.utcnow(),
				'pictureURL': pictureURL,
				'message': message
			}
		).inserted_id

	@staticmethod
	def getSpottedBySpottedId(spottedId):
		"""Gets a spotted by spottedId.
		"""
		if isinstance(spottedId, ObjectId):
			spottedId = ObjectId(spottedId)
		
		return mongo.db.spotteds.find_one({'_id': spottedId, 'archived': False}, projection={'archived': False})

	@staticmethod
	def getSpotteds(minLat, minLong, maxLat, maxLong, locationOnly):
		"""Gets a list of spotteds by using the latitude, longitude and radius.
		locationOnly returns only get the location of the returned spotteds if true.
		"""
		projection = {}
		projection['_id'] = True
		projection['location'] = True

		if not locationOnly:
			projection['anonymity'] = True
			projection['archived'] = True
			projection['creationDate'] = True
			projection['message'] = True
			projection['userId'] = True

		return [spotted for spotted in mongo.db.spotteds.find(
				{
					'archived': False,
					'location': {
						'$geoWithin': {
							'$geometry': {
								'type': 'Polygon',
								'coordinates': [
									[
										[float(minLat), float(minLong)],
										[float(minLat), float(maxLong)],
										[float(maxLat), float(maxLong)],
										[float(maxLat), float(minLong)],
										[float(minLat), float(minLong)]
									]
								]
							}
						}
					}
				},
				limit=200,
				projection=projection
			)
		]
		
	@staticmethod
	def getMySpotteds(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		return [x for x in mongo.db.spotteds.find({'userId': userId}, limit=20, projection={'archived': False})]

	@staticmethod
	def getSpottedsByUserId(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		res = [x for x in mongo.db.spotteds.find({'userId': userId, 'anonymity': False, 'archived': False}, limit=20, projection={'archived': False})]
		return res

class UserModel(object):

	@staticmethod
	def _createUser(facebookToken=None, googleToken=None):
		facebookId = None
		googleId = None
		facebookDate = None
		googleDate = None
		fullName = None
		profilPictureURL = None

		if not facebookToken == None:
			facebookId = facebookToken['user_id']
			url = "https://graph.facebook.com/{facebookId}?fields=name,picture&access_token={accessToken}"
			res = urllib2.urlopen(url.format(facebookId=facebookId,accessToken=facebookToken['token']))
			data = json.loads(res.read())
			profilPictureURL = data['picture']['data']['url']
			fullName = data['name']
			facebookDate = datetime.datetime.utcnow()
		
		if not googleToken == None:
			googleId = googleToken['sub']
			profilPictureURL = googleToken['picture']
			fullName = googleToken['name']
			googleDate = datetime.datetime.utcnow()

		userId = False

		if facebookId or googleId:
			userId = mongo.db.users.insert_one(
				{
					'facebookId': facebookId,
					'googleId': googleId,
					'fullName': fullName,
					'profilPictureURL': profilPictureURL,
					'disabled': False,
					'creationDate' : datetime.datetime.utcnow(),
					'facebookDate' : facebookDate,
					'googleDate' : googleDate,
				}
			).inserted_id

		return userId

	@staticmethod
	def _disableUser(userId, disabled):
		res = False
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		if mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': disabled}}).modified_count == 1:
			if mongo.db.spotteds.count({'userId': userId}) == mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': disabled}}).modified_count:
				res = True
			else:
				# Reverte
				mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': not disabled}})
				mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': not disabled}})
		return res

	@staticmethod
	def _getUser(filters):
		return mongo.db.users.find_one(filters)

	@staticmethod
	def _isDisabled(filters):
		res = True

		user = mongo.db.users.find_one(filters)
		if user and not user['disabled']:
			res = False

		return res

	@staticmethod
	def _linkToUserId(userId, filters):
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return mongo.db.users.update_one({'_id': userId}, filters).modified_count == 1

	@staticmethod
	def disableUser(userId):
		"""Disable a user
		"""
		return UserModel._disableUser(userId, True)

	@staticmethod
	def doesUserExist(userId):
		"""Checks if a user exists by userId.
		"""
		return True if UserModel.getUser(userId) else False

	@staticmethod
	def enableUser(userId):
		"""Enable a user
		"""
		return UserModel._disableUser(userId, False)

	@staticmethod
	def getUser(userId):
		"""Gets a user by userId.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return UserModel._getUser({'_id': userId})

	@staticmethod
	def isDisabled(userId):
		"""Check if a user is disabled
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return UserModel._isDisabled({'_id': userId})

	@staticmethod
	def mergeUsers(primaryUserId, userIdToMerge):
		"""Merge a Nearby account to another Nearby account with different service providers
		"""
		res = False
		if isinstance(primaryUserId, ObjectId):
			primaryUserId = ObjectId(primaryUserId)

		if isinstance(userIdToMerge, ObjectId):
			userIdToMerge = ObjectId(userIdToMerge)

		userToMerge = UserModel.getUser(primaryUserId)
		primaryUser = UserModel.getUser(userIdToMerge)

		if userToMerge and primaryUser \
		and (not userToMerge['facebookId'] and primaryUser['facebookId'] and not primaryUser['googleId'] \
		or not userToMerge['googleId'] and primaryUser['googleId'] and not primaryUser['facebookId']):
			if not userToMerge['facebookId'] and primaryUser['facebookId']:
				if mongo.db.users.update_one({'_id': primaryUserId}, {'facebookId': primaryUser['facebookId'], 'facebookDate': datetime.datetime.utcnow()}).modified_count == 1:
					res = True

			elif not userToMerge['googleId'] and primaryUser['googleId']:
				if mongo.db.users.update_one({'_id': primaryUserId}, {'googleId': primaryUser['googleId'], 'googleDate': datetime.datetime.utcnow()}).modified_count == 1:
					res = True

			if res:
				mongo.db.spotteds.update_many({'userId': userIdToMerge}, {'userId': primaryUserId})

		return res


class FacebookModel(UserModel):

	@staticmethod
	def createUser(facebookToken):
		"""Creates a user related to a facebookToken.
		"""
		return UserModel._createUser(facebookToken=facebookToken)

	@staticmethod
	def doesUserExist(facebookId):
		"""Checks if a user exists by facebookId.
		"""
		return True if FacebookModel.getUser(facebookId) else False

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
	def getUser(facebookId):
		"""Gets a user by facebookId.
		"""
		return UserModel._getUser({'facebookId': facebookId})

	@staticmethod
	def isDisabled(facebookId):
		"""Check if a Facebook user is disabled
		"""
		return UserModel._isDisabled({'facebookId': facebookId})

	@staticmethod
	def linkToUserId(userId, facebookId):
		"""Register a Facebook account to a user.
		"""
		return UserModel._linkToUserId(userId, {'facebookId': facebookId})

class GoogleModel(UserModel):

	@staticmethod
	def createUser(googleToken):
		"""Creates a user related to a googleToken.
		"""
		return UserModel._createUser(googleToken=googleToken)

	@staticmethod
	def doesUserExist(googleId):
		"""Checks if a user exists by googleId.
		"""
		return True if GoogleModel.getUser(googleId) else False

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
	def getUser(googleId):
		"""Gets a user by googleId.
		"""
		return UserModel._getUser({'googleId': googleId})

	@staticmethod
	def isDisabled(googleId):
		"""Check if a Google user is disabled
		"""
		return UserModel._isDisabled({'googleId': googleId})

	@staticmethod
	def linkToUserId(userId, googleId):
		"""Register a Google account to a user.
		"""
		return UserModel._linkToUserId(userId, {'googleId': googleId})
