#!/usr/bin/env python
import json
import math
import urllib2

from uuid import uuid4
from bson import ObjectId

from app import mongo

from botocore.exceptions import ClientError
from oauth2client import client, crypt

class SpottedModel(object):

	@staticmethod
	def createSpotted(userId, anonymity, latitude, longitude, message, picture=None):
		"""Creates a spotted.
		"""
		if not picture is None:
			# Save it to S3, then keep the picture link to save it in the table.
			pass

		return mongo.db.spotteds.insert_one(
			{
				'userId': userId,
				'location': {
					'type':'Point',
					'coordinates': [
						float(latitude), 
						float(longitude)
					]
				},
				'anonymity': anonymity,
				'isArchived': False,
				# Add save date
				# Add picture link here
				'message': message
			}
		).inserted_id

	@staticmethod
	def getSpottedBySpottedId(spottedId):
		"""Gets a spotted by spottedId.
		"""
		return mongo.db.spotteds.find_one({'_id': ObjectId(spottedId)})

	@staticmethod
	def getSpotteds(minLat, minLong, maxLat, maxLong, locationOnly):
		"""Gets a list of spotteds by using the latitude, longitude and radius.
		locationOnly returns only get the location of the returned spotteds if true.
		"""
		return [x for x in mongo.db.spotteds.find(
				{
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
				}
			)
		]

	@staticmethod
	def getMySpotteds(userId):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		return [x for x in mongo.db.spotteds.find({'userId': ObjectId(userId)})]

	@staticmethod
	def getSpottedsByUserId(userId, anonymity=False):
		"""Gets a list of spotteds by using the userId of a specific user.
		"""
		res = []
		if anonymity is None:
			res = [x for x in mongo.db.spotteds.find({'userId': ObjectId(userId)})]
		else:
			res = [x for x in mongo.db.spotteds.find({'userId': ObjectId(userId), 'anonymity': anonymity})]
		return res

class UserModel(object):

	@staticmethod
	def createUser(facebookToken=None, googleToken=None):
		"""THIS METHOD SHOULDN'T BE USED ELSEWHERE THAN IN FacebookModel AND GoogleModel.
		Creates a user with either facebookToken or googleToken.
		"""
		facebookId = None
		googleId = None
		fullName = None
		profilPictureURL = None

		if not facebookToken == None:
			facebookId = facebookToken['user_id']
			url = "https://graph.facebook.com/{facebookId}?fields=name,picture&access_token={accessToken}"
			res = urllib2.urlopen(url.format(facebookId=facebookId,accessToken=facebookToken['token']))
			data = json.loads(res.read())
			profilPictureURL = data['picture']['data']['url']
			fullName = data['name']
		
		if not googleToken == None:
			googleId = googleToken['sub']
			profilPictureURL = googleToken['picture']
			fullName = googleToken['name']

		userId = False

		if facebookId or googleId:
			userId = mongo.db.users.insert_one(
				{
					'facebookId': facebookId,
					'googleId': googleId,
					'fullName': fullName,
					'profilPictureURL': profilPictureURL,
					'disabled': False
				}
			).inserted_id

		return userId

	@staticmethod
	def disableUser(userId):
		res = False
		if mongo.db.users.update_one({'_id': userId}, {'disabled': True}).modified_coun == 1:
			mongo.db.spotteds.update_many({'userId': userId}, {'isArchived': True})
			res = True
		return res


	@staticmethod
	def doesUserExist(userId):
		"""Checks if a user exists by userId.
		"""
		return True if UserModel.getUser(userId) else False

	@staticmethod
	def getUser(userId):
		"""Gets a user by userId.
		"""
		return mongo.db.users.find_one({'_id': ObjectId(userId)})

	@staticmethod
	def mergeUsers(userIdFrom, userIdTo):
		res = False
		userTo = UserModel.getUser(userIdFrom)
		userFrom = UserModel.getUser(userIdTo)

		if userTo and userFrom \
		and (not userTo['facebookId'] and userFrom['facebookId'] and not userFrom['googleId'] \
		or not userTo['googleId'] and userFrom['googleId'] and not userFrom['facebookId']):
			mongo.db.spotteds.update_many({'userId': userIdTo}, {'userId': userIdFrom})
			if not userTo['facebookId'] and userFrom['facebookId']:
				mongo.db.users.update_one({'_id': userIdFrom}, {'facebookId': userFrom['facebookId']})

			elif not userTo['googleId'] and userFrom['googleId']:
				mongo.db.users.update_one({'_id': userIdFrom}, {'googleId': userFrom['googleId']})
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
		return mongo.db.users.find_one({'facebookId': facebookId})

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
			if user and FacebookModel.validateUserIdAndFacebookIdLink(userId, None):
				res = mongo.db.users.update_one({'_id': userId}, {'facebookId': facebookId}).modified_count == 1

		return res

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
		return mongo.db.users.find_one({'googleId': googleId})

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
			if user and GoogleModel.validateUserIdAndGoogleIdLink(userId, None):
				res = mongo.db.users.update_one({'_id': userId}, {'googleId': googleId}).modified_count == 1
		
		return res

	@staticmethod
	def validateUserIdAndGoogleIdLink(userId, googleId):
		"""Validate the link between a user and a Google account.
		"""
		res = False
		user = UserModel.getUser(userId)
		if user and user['googleId'] == googleId:
			res = True

		return res
