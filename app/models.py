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
					'anonymity': False,
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
	def createUser(facebookToken=None, googleToken=None):
		"""THIS METHOD SHOULDN'T BE USED ELSEWHERE THAN IN FacebookModel AND GoogleModel.
		Creates a user with either facebookToken or googleToken.
		"""
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
	def disableUser(userId):
		res = False
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		if mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': True}}).modified_count == 1:
			if mongo.db.spotteds.count({'userId': userId}) == mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': True}}).modified_count:
				res = True
			else:
				# Reverte
				mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': False}})
				mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': False}})
		return res

	@staticmethod
	def doesUserExist(userId):
		"""Checks if a user exists by userId.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return True if UserModel.getUser(userId) else False

	@staticmethod
	def enableUser(userId):
		res = False
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		if mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': False}}).modified_count == 1:
			if mongo.db.spotteds.count({'userId': userId}) == mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': False}}).modified_count:
				res = True
			else:
				# Reverte
				mongo.db.users.update_one({'_id': userId}, {'$set': {'disabled': True}})
				mongo.db.spotteds.update_many({'userId': userId}, {'$set': {'archived': True}})
		return res

	@staticmethod
	def getUser(userId):
		"""Gets a user by userId.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		return mongo.db.users.find_one({'_id': userId})

	@staticmethod
	def isDisabled(userId):
		res = True
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)
		
		user = mongo.db.users.find_one({'_id': userId})
		if user and not user.disabled:
			res = False

		return res

	@staticmethod
	def mergeUsers(userIdNew, userIdOld):
		res = False
		if isinstance(userIdNew, ObjectId):
			userIdNew = ObjectId(userIdNew)

		if isinstance(userIdOld, ObjectId):
			userIdOld = ObjectId(userIdOld)

		userOld = UserModel.getUser(userIdNew)
		userNew = UserModel.getUser(userIdOld)

		if userOld and userNew \
		and (not userOld['facebookId'] and userNew['facebookId'] and not userNew['googleId'] \
		or not userOld['googleId'] and userNew['googleId'] and not userNew['facebookId']):
			if not userOld['facebookId'] and userNew['facebookId']:
				if mongo.db.users.update_one({'_id': userIdNew}, {'facebookId': userNew['facebookId'], 'facebookDate': datetime.datetime.utcnow()}).modified_count == 1:
					res = True

			elif not userOld['googleId'] and userNew['googleId']:
				if mongo.db.users.update_one({'_id': userIdNew}, {'googleId': userNew['googleId'], 'googleDate': datetime.datetime.utcnow()}).modified_count == 1:
					res = True

			if res:
				mongo.db.spotteds.update_many({'userId': userIdOld}, {'userId': userIdNew})

		return res


class FacebookModel(UserModel):

	@staticmethod
	def createUserWithFacebook(facebookToken):
		"""Creates a user related to a facebookToken.
		"""
		return UserModel.createUser(facebookToken=facebookToken)

	@staticmethod
	def doesFacebookIdExist(facebookId):
		"""Checks if a user exists by facebookId.
		"""
		return True if FacebookModel.getUserByFacebookId(facebookId) else False

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
		return mongo.db.users.find_one({'facebookId': facebookId})

	@staticmethod
	def linkFacebookIdToUserId(userId, facebookId):
		"""Register a Facebook account to a user.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return mongo.db.users.update_one({'_id': userId}, {'facebookId': facebookId}).modified_count == 1

class GoogleModel(UserModel):

	@staticmethod
	def createUserWithGoogle(googleToken):
		"""Creates a user related to a googleToken.
		"""
		return UserModel.createUser(googleToken=googleToken)

	@staticmethod
	def doesGoogleIdExist(googleId):
		"""Checks if a user exists by googleId.
		"""
		return True if GoogleModel.getUserByGoogleId(googleId) else False

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
		return mongo.db.users.find_one({'googleId': googleId})

	@staticmethod
	def linkGoogleIdToUserId(userId, googleId):
		"""Register a Google account to a user.
		"""
		if isinstance(userId, ObjectId):
			userId = ObjectId(userId)

		return mongo.db.users.update_one({'_id': userId}, {'googleId': googleId}).modified_count == 1
