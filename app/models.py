#!/usr/bin/env python
import json
import urllib2
import datetime

from bson import ObjectId
from flask_pymongo import DESCENDING
from oauth2client import client, crypt

from app import mongo
from app.s3connection import S3Connection

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonymity, longitude, latitude, message, picture=None):
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
						float(longitude),
						float(latitude)
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
		if not isinstance(spottedId, ObjectId):
			spottedId = ObjectId(spottedId)
		
		spotted = mongo.db.spotteds.find_one({'_id': spottedId, 'archived': False}, projection={'archived': False})

		if spotted and spotted['anonymity']:
			spotted['userId'] = None
		
		return spotted

	@staticmethod
	def getSpotteds(minLong, minLat, maxLong, maxLat, locationOnly):
		"""Gets a list of spotteds by using the latitude, longitude and radius.
		locationOnly returns only get the location of the returned spotteds if true.
		"""
		projection = {}
		projection['_id'] = True
		projection['location'] = True
		projection['creationDate'] = True
		limit = 1000

		if not locationOnly:
			projection['anonymity'] = True
			projection['archived'] = True
			projection['message'] = True
			projection['userId'] = True
			limit = 200

		spotteds = [spotted for spotted in mongo.db.spotteds.find(
				{
					'archived': False,
					'location': {
						'$geoWithin': {
							'$geometry': {
								'type': 'Polygon',
								'coordinates': [
									[
										[float(minLong), float(minLat)],
										[float(minLong), float(maxLat)],
										[float(maxLong), float(maxLat)],
										[float(maxLong), float(minLat)],
										[float(minLong), float(minLat)]
									]
								]
							}
						}
					}
				},
				limit=limit,
				projection=projection,
				sort=[('creationDate', DESCENDING)]
			)
		]

		if not locationOnly:
			for spotted in spotteds:
				if spotted['anonymity']:
					spotted['userId'] = None

		return spotteds
		
	@staticmethod
	def getMySpotteds(userId, skip=None, since=None):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		if skip is None:
			skip = 0

		if since:
			spotteds = [spotted for spotted in mongo.db.spotteds.find({'userId': userId, 'creationDate': {'$gte': since}}, skip=skip, limit=20, projection={'archived': False}, sort=[('creationDate', DESCENDING)])]
		else:
			spotteds = [spotted for spotted in mongo.db.spotteds.find({'userId': userId}, skip=skip, limit=20, projection={'archived': False}, sort=[('creationDate', DESCENDING)])]

		return spotteds

	@staticmethod
	def getSpottedsByUserId(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		spotteds = [spotted for spotted in mongo.db.spotteds.find({'userId': userId, 'anonymity': False, 'archived': False}, limit=20, projection={'archived': False}, sort=[('creationDate', DESCENDING)])]
		
		for spotted in spotteds:
			if spotted['anonymity']:
				spotted['userId'] = None

		return spotteds

class UserModel(object):

	@staticmethod
	def _createUser(facebookToken=None, googleToken=None):
		userId = False

		if not facebookToken or not googleToken:
			creationDate = datetime.datetime.utcnow()

			insert = {
				'disabled': False,
				'creationDate' : creationDate,
				'googleDate' : None,
				'googleId' : None,
				'facebookDate' : None,
				'facebookId' : None
			}

			if not facebookToken is None:
				insert['facebookDate'] = creationDate
				insert['facebookId'] = facebookToken['user_id']
				url = "https://graph.facebook.com/{facebookId}?fields=name,picture&access_token={accessToken}"
				res = urllib2.urlopen(url.format(facebookId=insert['facebookId'],accessToken=facebookToken['token']))
				data = json.loads(res.read())
				insert['profilePictureURL'] = data['picture']['data']['url']
				insert['fullName'] = data['name']
			
			if not googleToken is None:
				insert['googleDate'] = creationDate
				insert['googleId'] = googleToken['sub']
				insert['profilePictureURL'] = googleToken['picture']
				insert['fullName'] = googleToken['name']

			if not insert['facebookId'] is None or not insert['googleId'] is None:
				userId = mongo.db.users.insert_one(insert).inserted_id

		return userId

	@staticmethod
	def _disableUser(userId, disabled):
		res = False
		if not isinstance(userId, ObjectId):
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
	def _getUser(filters, projection=None):
		return mongo.db.users.find_one(filters, projection=projection)

	@staticmethod
	def _isDisabled(filters):
		res = True

		user = mongo.db.users.find_one(filters)
		if user and not user['disabled']:
			res = False

		return res

	@staticmethod
	def _linkToUserId(userId, replace):
		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return mongo.db.users.update_one({'_id': userId}, replace).modified_count == 1

	@staticmethod
	def disableUser(userId):
		"""Disable a user
		"""
		return UserModel._disableUser(userId=userId, disabled=True)

	@staticmethod
	def doesUserExist(userId):
		"""Checks if a user exists by userId.
		"""
		return True if UserModel.getUser(userId=userId) else False

	@staticmethod
	def enableUser(userId):
		"""Enable a user
		"""
		return UserModel._disableUser(userId=userId, disabled=False)

	@staticmethod
	def getUser(userId, publicInfo=False):
		"""Gets a user by userId.
		"""
		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		projection = None
		if publicInfo:
			projection = {'_id': 0, 'profilePictureURL': 1, 'fullName': 1}

		return UserModel._getUser(filters={'_id': userId}, projection=projection)

	@staticmethod
	def isDisabled(userId):
		"""Check if a user is disabled
		"""
		if not isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return UserModel._isDisabled(filters={'_id': userId})

	@staticmethod
	def mergeUsers(primaryUserId, userIdToMerge):
		"""Merge a Nearby account to another Nearby account with different service providers
		"""
		res = False
		if not isinstance(primaryUserId, ObjectId):
			primaryUserId = ObjectId(primaryUserId)

		if not isinstance(userIdToMerge, ObjectId):
			userIdToMerge = ObjectId(userIdToMerge)

		userToMerge = UserModel.getUser(userId=primaryUserId)
		primaryUser = UserModel.getUser(userId=userIdToMerge)

		if userToMerge and primaryUser \
		and (not userToMerge['facebookId'] and primaryUser['facebookId'] and not primaryUser['googleId'] \
		or not userToMerge['googleId'] and primaryUser['googleId'] and not primaryUser['facebookId']):
			if not userToMerge['facebookId'] and primaryUser['facebookId']:
				if mongo.db.users.update_one({'_id': primaryUserId}, {'$set': {'facebookId': primaryUser['facebookId'], 'facebookDate': datetime.datetime.utcnow()}}).modified_count == 1:
					res = True

			elif not userToMerge['googleId'] and primaryUser['googleId']:
				if mongo.db.users.update_one({'_id': primaryUserId}, {'$set': {'googleId': primaryUser['googleId'], 'googleDate': datetime.datetime.utcnow()}}).modified_count == 1:
					res = True

			if res:
				mongo.db.spotteds.update_many({'userId': userIdToMerge}, {'$set': {'userId': primaryUserId}})

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
		return True if FacebookModel.getUser(facebookId=facebookId) else False

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
		return UserModel._getUser(filters={'facebookId': facebookId})

	@staticmethod
	def isDisabled(facebookId):
		"""Check if a Facebook user is disabled
		"""
		return UserModel._isDisabled(filters={'facebookId': facebookId})

	@staticmethod
	def linkToUserId(userId, facebookId):
		"""Register a Facebook account to a user.
		"""
		return UserModel._linkToUserId(userId=userId, replace={'facebookId': facebookId})

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
		return True if GoogleModel.getUser(googleId=googleId) else False

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
		return UserModel._getUser(filters={'googleId': googleId})

	@staticmethod
	def isDisabled(googleId):
		"""Check if a Google user is disabled
		"""
		return UserModel._isDisabled(filters={'googleId': googleId})

	@staticmethod
	def linkToUserId(userId, googleId):
		"""Register a Google account to a user.
		"""
		return UserModel._linkToUserId(userId=userId, replace={'googleId': googleId})
