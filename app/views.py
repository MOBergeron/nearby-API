#!/usr/bin/env python
import json

from functools import wraps

from app import app, mongo

from app.forms import ContactForm, CreateSpottedForm, GetMySpottedsForm, GetSpottedsForm, MergeFacebookForm, MergeGoogleForm, LinkFacebookForm, LinkGoogleForm
from app.models import SpottedModel, UserModel, FacebookModel, GoogleModel
from app.utils import CustomJSONEncoder, validateObjectId

from flask import g, abort, request, Response
from flask_cors import cross_origin

# Decorators
def requireAuthenticate(acceptGuest):
	def requireAuth(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			auth = request.authorization
			if auth:
				if acceptGuest and request.headers['Service-Provider'] == 'Guest' and auth.username == app.config['GUEST_ID']:
					if auth.password == app.config['GUEST_TOKEN']:
						g.currentUser = None
						g.loginWith = 'Guest'
						return f(*args, **kwargs)
				else:
					g.loginWith = None
					if request.headers['Service-Provider'] == 'Facebook':
						g.facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], auth.password)
						if g.facebookToken['is_valid'] and g.facebookToken['user_id'] == auth.username:
							g.currentUser = FacebookModel.getUser(auth.username)
							g.loginWith = 'Facebook'
					elif request.headers['Service-Provider'] == 'Google':
						g.googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], auth.password)
						if g.googleToken and g.googleToken['sub'] == auth.username:
							g.currentUser = GoogleModel.getUser(auth.username)
							g.loginWith = 'Google'
					
					if g.loginWith and (str(request.url_rule) == '/v1/login' or g.currentUser):
						if str(request.url_rule) == '/v1/login' or not g.currentUser['disabled']:
							return f(*args, **kwargs)
						return abort(410)
			return abort(401)
		return decorated_function
	return requireAuth

@app.errorhandler(400)
def badRequest(e):
	return Response(json.dumps({'error':'Bad Request'}), status=400, mimetype="application/json")

@app.errorhandler(401)
def unauthorized(e):
	return Response(json.dumps({'error':'Unauthorized'}), status=401, mimetype="application/json")

@app.errorhandler(403)
def forbidden(e):
	return Response(json.dumps({'error':'Forbidden'}), status=403, mimetype="application/json")

@app.errorhandler(404)
def notFound(e):
	return Response(json.dumps({'error':'Not Found'}), status=404, mimetype="application/json")

@app.errorhandler(405)
def methodNotAllowed(e):
	return Response(json.dumps({'error':'Method Not Allowed'}), status=405, mimetype="application/json")

@app.errorhandler(410)
def gone(e):
	return Response(json.dumps({'error':'Gone'}), status=410, mimetype="application/json")

@app.errorhandler(500)
def internalServerError(e):
	return Response(json.dumps({'error':'Internal Server Error'}), status=500, mimetype="application/json")

@app.route("/v1/spotted", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def createSpotted():
	form = CreateSpottedForm()
	
	# Creates a spotted according to form data
	if form.validate():
		anonymity = form.anonymity.data
		longitude = form.longitude.data
		latitude = form.latitude.data
		message = form.message.data
		picture = form.picture.data

		res = SpottedModel.createSpotted(userId=g.currentUser['_id'], anonymity=anonymity, longitude=longitude, latitude=latitude, message=message, picture=picture)
		if res:
			return Response(json.dumps({'result': res}, cls=CustomJSONEncoder), status=201, mimetype="application/json")

	return abort(400)

@app.route("/v1/disable", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def disableAccount():
	if UserModel.disableUser(g.currentUser['_id']):
		return json.dumps({'result':'OK'}), 200

	return abort(400)

@app.route("/v1/link/facebook", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def linkFacebook():
	"""Links a Facebook account to an existing Google account.
	"""
	form = LinkFacebookForm()
	# Check if the Service-Provider is Google
	if form.validate_on_submit() and g.loginWith == 'Google' and g.currentUser['facebookId'] is None:
		facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], form.token.data)
		if facebookToken['is_valid'] and facebookToken['user_id'] == form.facebookId.data:
			# Continue only if the account doesn't exist yet.
			if not FacebookModel.doesUserExist(form.facebookId.data):
				if FacebookModel.linkToUserId(g.currentUser['_id'], form.facebookId.data):
					return json.dumps({'result':'OK'}), 200
			else:
				return abort(403)
		else:
			return abort(401)

	return abort(400)

@app.route("/v1/link/google", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def linkGoogle():
	"""Links a Google account to an existing Facebook account.
	"""
	form = LinkGoogleForm()
	# Check if the Service-Provider is Facebook
	if form.validate_on_submit() and g.loginWith == 'Facebook' and g.currentUser['googleId'] is None:
		googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], form.token.data)
		if googleToken and googleToken['sub'] == form.googleId.data:
			# Continue only if the account doesn't exist yet.
			if not GoogleModel.doesUserExist(form.googleId.data):
				if GoogleModel.linkToUserId(g.currentUser['_id'], form.googleId.data):
					return json.dumps({'result':'OK'}), 200
			else:
				return abort(403)
		else:
			return abort(401)

	return abort(400)

@app.route("/v1/login", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def loginFacebook():
	if g.loginWith == 'Facebook':
		if not FacebookModel.doesUserExist(request.authorization.username):
			if FacebookModel.createUser(g.facebookToken):
				return json.dumps({'result':'Created'}), 201

		elif FacebookModel.isDisabled(request.authorization.username):
			user = FacebookModel.getUser(request.authorization.username)
			if user:
				if UserModel.enableUser(user['_id']):
					return json.dumps({'result':'OK'}), 200
		else:
			return json.dumps({'result':'OK'}), 200

	elif g.loginWith == 'Google':
		if not GoogleModel.doesUserExist(request.authorization.username):
			if GoogleModel.createUser(g.googleToken):
				return json.dumps({'result':'Created'}), 201

		elif GoogleModel.isDisabled(request.authorization.username):
			user = GoogleModel.getUser(request.authorization.username)
			if user:
				if UserModel.enableUser(user['_id']):
					return json.dumps({'result':'OK'}), 200
		else:
			return json.dumps({'result':'OK'}), 200
		
	return abort(400)

@app.route("/v1/merge/facebook", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def mergeFacebook():
	"""Merges an existing Facebook account to an existing Google account.
	"""
	form = MergeFacebookForm()
	# Check if the Service-Provider is Google
	if form.validate_on_submit() and g.loginWith == 'Google' and g.currentUser['facebookId'] is None:
		facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], form.token.data)
		if facebookToken['is_valid'] and facebookToken['user_id'] == form.facebookId.data:
			# Continue only if the account does exist.
			if FacebookModel.doesUserExist(form.facebookId.data):
				facebookUser = FacebookModel.getUser(form.facebookId.data)
				if UserModel.mergeUsers(g.currentUser['_id'], facebookUser['_id']):
					return json.dumps({'result':'OK'}), 200
			else:
				return abort(404)
		else:
			return abort(401)

	return abort(400)

@app.route("/v1/merge/google", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def mergeGoogle():
	"""Merges an existing Google account to an existing Facebook account.
	"""
	form = MergeGoogleForm()
	# Check if the Service-Provider is Facebook
	if form.validate_on_submit() and g.loginWith == 'Facebook' and g.currentUser['googleId'] is None:
		googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], form.token.data)
		if googleToken and googleToken['sub'] == form.googleId.data:
			# Continue only if the account does exist.
			if GoogleModel.doesUserExist(form.googleId.data):
				googleUser = GoogleModel.getUser(form.googleId.data)
				if UserModel.mergeUsers(g.currentUser['_id'], googleUser['_id']):
					return json.dumps({'result':'OK'}), 200
			else:
				return abort(404)
		else:
			return abort(401)

	return abort(400)

@app.route("/v1/spotted/<spottedId>", methods=['GET'])
@cross_origin(origin="*")
@requireAuthenticate(acceptGuest=True)
def spotted(spottedId):
	# Returns a specific spotted
	if spottedId and validateObjectId(spottedId):
		spotted = SpottedModel.getSpottedBySpottedId(spottedId)
		if spotted:
			if not spotted['anonymity'] or not g.loginWith == 'Guest' and spotted['userId'] == g.currentUser['_id']:
				user = UserModel.getUser(spotted['userId'], publicInfo=True)
				if user:
					spotted.update(user)

			response = Response(json.dumps(spotted, cls=CustomJSONEncoder), status=200, mimetype="application/json")
			return response
		else:
			return abort(404)

	return abort(400)

@app.route("/v1/spotteds", methods=['GET'])
@cross_origin(origin="*")
@requireAuthenticate(acceptGuest=True)
def spotteds():
	form = GetSpottedsForm(request.args)

	# Returns all corresponding spotteds according to arguments
	if form.validate():
		minLat = form.minLat.data
		minLong = form.minLong.data
		maxLat = form.maxLat.data
		maxLong = form.maxLong.data
		locationOnly = form.locationOnly.data

		# If locationOnly is True, returns only the locations for all the spotteds.
		# Else, returns all spotteds with their whole data.
		res = SpottedModel.getSpotteds(minLong=minLong, minLat=minLat, maxLong=maxLong, maxLat=maxLat, locationOnly=locationOnly)
		if type(res) == list:
			response = Response(json.dumps(res, cls=CustomJSONEncoder), status=200, mimetype="application/json")
			return response

	return abort(400)

@app.route("/v1/spotteds/<userId>", methods=['GET'])
@requireAuthenticate(acceptGuest=False)
def spottedsByUserId(userId):
	# Returns all spotteds to a specific userId
	if userId and (validateObjectId(userId) or userId == 'me'):
		res = None
		if userId == 'me':
			form = GetMySpottedsForm(request.args)
			if form.validate():
				skip = form.skip.data
				since = form.since.data
				res = SpottedModel.getMySpotteds(g.currentUser['_id'], skip=skip, since=since)
		elif str(g.currentUser['_id'])  == userId:
			res = SpottedModel.getMySpotteds(userId)
		else:
			res = SpottedModel.getSpottedsByUserId(userId)

		if type(res) == list:
			return Response(json.dumps(res, cls=CustomJSONEncoder), status=200, mimetype="application/json")

	return abort(400)

@app.route("/v1/user/<userId>", methods=['GET'])
@cross_origin(origin="*")
@requireAuthenticate(acceptGuest=True)
def userByUserId(userId):
	# Returns info about a specific user
	if userId and (validateObjectId(userId) or userId == 'me'):
		user = None
		if userId == 'me' and g.currentUser:
			user = UserModel.getUser(g.currentUser['_id'])
		elif str(g.currentUser['_id'])  == userId:
			user = UserModel.getUser(userId)
		else:
			user = UserModel.getUser(userId, publicInfo=True)

		if user:
			return Response(json.dumps(user, cls=CustomJSONEncoder), status=200, mimetype="application/json")
		
		return abort(404)

	return abort(400)
