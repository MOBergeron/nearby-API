#!/usr/bin/env python
import json

from functools import wraps

from app import app, mongo

from app.forms import ContactForm, CreateSpottedForm, GetSpottedsForm, MergeFacebookForm, MergeGoogleForm, LinkFacebookForm, LinkGoogleForm
from app.models import SpottedModel, UserModel, FacebookModel, GoogleModel
from app.utils import ObjectIdEncoder, validateUuid

from flask import g, abort, request, Response

ALLOW_CROSS_ORIGIN_FROM = ["https://nearbyapp.github.io"]

# Decorators
def requireAuthenticate(acceptGuest):
	def requireAuth(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			auth = request.authorization
			if auth:
				if acceptGuest and request.headers['Service-Provider'] == 'Guest' and auth.username == app.config['GUEST_ID']:
					if auth.password == app.config['GUEST_TOKEN']:
						g.loginWith = 'Guest'
						return f(*args, **kwargs)
				else:
					if request.headers['Service-Provider'] == 'Facebook':
						g.facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], auth.password)
						if g.facebookToken['is_valid'] and g.facebookToken['user_id'] == auth.username:
							if str(request.url_rule) == '/v1/login' or FacebookModel.doesFacebookIdExist(auth.username):
								g.loginWith = 'Facebook'
								return f(*args, **kwargs)
					elif request.headers['Service-Provider'] == 'Google':
						g.googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], auth.password)
						if g.googleToken and g.googleToken['sub'] == auth.username:
							if str(request.url_rule) == '/v1/login' or GoogleModel.doesGoogleIdExist(auth.username):
								g.loginWith = 'Google'	
								return f(*args, **kwargs)
			return abort(401)
		return decorated_function
	return requireAuth

def allowCrossOrigin(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'Origin' in request.headers:
			if request.headers['Origin'] in ALLOW_CROSS_ORIGIN_FROM:
				res = f(*args, **kwargs)
				res.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
				return res
			return abort(403)
		return f(*args, **kwargs)
	return decorated_function

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

@app.errorhandler(500)
def internalServerError(e):
	return Response(json.dumps({'error':'Internal Server Error'}), status=500, mimetype="application/json")

@app.route("/test")
def test():
	output = []
	for s in mongo.db.users.find():
		output.append(s)
	return json.dumps(output, cls=ObjectIdEncoder)

@app.route("/v1/login", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def loginFacebook():
	if g.loginWith == 'Facebook':
		if not FacebookModel.doesFacebookIdExist(request.authorization.username):
			if FacebookModel.createUserWithFacebook(g.facebookToken):
				return json.dumps({'result':'Created'}), 201
		else:
			return json.dumps({'result':'OK'}), 200

	elif g.loginWith == 'Google':
		if not GoogleModel.doesGoogleIdExist(request.authorization.username):
			if GoogleModel.createUserWithGoogle(g.googleToken):
				return json.dumps({'result':'Created'}), 201
		else:
			return json.dumps({'result':'OK'}), 200
		
	return abort(400)

#@app.route("/v1/disable/facebook", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def disableFacebook():
	pass

#@app.route("/v1/disable/google", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def disableGoogle():
	pass

#@app.route("/v1/merge/facebook", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def mergeFacebook():
	"""Merges an existing Facebook account to an existing Google account.
	"""
	form = MergeFacebookForm()
	# Check if the Service-Provider is Google
	if form.validate_on_submit() and g.loginWith == 'Google':
		facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], form.token.data)
		if facebookToken['is_valid'] and facebookToken['user_id'] == form.facebookId.data:
			# Continue only if the account doesn't exist yet.
			if FacebookModel.doesFacebookIdExist(form.facebookId.data):
				googleUser = GoogleModel.getUserByGoogleId(request.authorization.username)
				facebookUser = FacebookModel.getUserByFacebookId(form.facebookId.data)

				if googleUser and googleUser['facebookId'] == 'unset':
					if UserModel.mergeUsers(facebookUser['userId'], googleUser['userId']):
						return json.dumps({'result':'OK'}), 200

	return abort(400)

#@app.route("/v1/merge/google", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def mergeGoogle():
	"""Merges an existing Google account to an existing Facebook account.
	"""
	form = MergeGoogleForm()
	# Check if the Service-Provider is Facebook
	if form.validate_on_submit() and g.loginWith == 'Facebook':
		googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], form.token.data)
		if googleToken and googleToken['sub'] == form.googleId.data:
			# Continue only if the account doesn't exist yet.
			if GoogleModel.doesGoogleIdExist(form.googleId.data):
				facebookUser = FacebookModel.getUserByFacebookId(request.authorization.username)
				googleUser = GoogleModel.getUserByGoogleId(form.googleId.data)

				if facebookUser and facebookUser['googleId'] == 'unset':
					if UserModel.mergeUsers(googleUser['userId'], facebookUser['userId']):
						return json.dumps({'result':'OK'}), 200

	return abort(400)

@app.route("/v1/link/facebook", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def linkFacebook():
	"""Links a Facebook account to an existing Google account.
	"""
	form = LinkFacebookForm()
	# Check if the Service-Provider is Google
	if form.validate_on_submit() and g.loginWith == 'Google':
		facebookToken = FacebookModel.getTokenValidation(app.config['FACEBOOK_ACCESS_TOKEN'], form.token.data)
		if facebookToken['is_valid'] and facebookToken['user_id'] == form.facebookId.data:
			# Continue only if the account doesn't exist yet.
			if not FacebookModel.doesFacebookIdExist(form.facebookId.data):
				user = GoogleModel.getUserByGoogleId(request.authorization.username)
				if user and user['facebookId'] == 'unset':
					if FacebookModel.linkFacebookIdToUserId(user['_id'], form.facebookId.data):
						return json.dumps({'result':'OK'}), 200
				else:
					return abort(403)
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
	if form.validate_on_submit() and g.loginWith == 'Facebook':
		googleToken = GoogleModel.getTokenValidation(app.config['GOOGLE_CLIENT_ID'], form.token.data)
		if googleToken and googleToken['sub'] == form.googleId.data:
			# Continue only if the account doesn't exist yet.
			if not GoogleModel.doesGoogleIdExist(form.googleId.data):
				user = FacebookModel.getUserByFacebookId(request.authorization.username)
				if user and user['googleId'] == 'unset':
					if GoogleModel.linkGoogleIdToUserId(user['_id'], form.googleId.data):
						return json.dumps({'result':'OK'}), 200
				else:
					return abort(403)
			else:
				return abort(403)
		else:
			return abort(401)

	return abort(400)

@app.route("/v1/spotted", methods=['POST'])
@requireAuthenticate(acceptGuest=False)
def createSpotted():
	form = CreateSpottedForm()
	
	# Creates a spotted according to form data
	if form.validate_on_submit():
		anonymity = form.anonymity.data
		longitude = form.longitude.data
		latitude = form.latitude.data
		message = form.message.data
		#picture = form.picture.data

		if g.loginWith == 'Facebook':
			user = FacebookModel.getUserByFacebookId(request.authorization.username)
		elif g.loginWith == 'Google':
			user = GoogleModel.getUserByGoogleId(request.authorization.username)

		if user:
			res = SpottedModel.createSpotted(userId=user['_id'], anonymity=anonymity, latitude=latitude, longitude=longitude, message=message, picture=None)
			if res:
				return Response(json.dumps({'result': res}, cls=ObjectIdEncoder), status=201, mimetype="application/json")
	
	return abort(400)

@app.route("/v1/spotted/<spottedId>", methods=['GET'])
@allowCrossOrigin
@requireAuthenticate(acceptGuest=True)
def spotted(spottedId):
	# Returns a specific spotted
	if spottedId:
		if validateUuid(spottedId):
			res = SpottedModel.getSpottedBySpottedId(spottedId)
			if res:
				response = Response(json.dumps(res, cls=ObjectIdEncoder))
				return response
			else:
				return abort(404)

	return abort(400)

@app.route("/v1/spotteds", methods=['GET'])
@allowCrossOrigin
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
		res = SpottedModel.getSpotteds(minLat=minLat, maxLat=maxLat, minLong=minLong, maxLong=maxLong, locationOnly=locationOnly)
		if type(res) == list:
			response = Response(json.dumps(res, cls=ObjectIdEncoder))
			return response

	return abort(400)

@app.route("/v1/spotteds/<userId>", methods=['GET'])
@requireAuthenticate(acceptGuest=False)
def spottedsByUserId(userId):
	# Returns all spotteds to a specific userId
	if userId and (validateUuid(userId) or userId == 'me'):
		res = False
		if userId == 'me':
			user = FacebookModel.getUserByFacebookId(request.authorization.username)
			if user:
				userId = user['_id']
				res = SpottedModel.getMySpotteds(userId)
		elif FacebookModel.validateUserIdAndFacebookIdLink(userId, request.authorization.username):
			res = SpottedModel.getSpottedsByUserId(userId)
			#res = SpottedModel.getMySpotteds(userId)		
		else:
			res = SpottedModel.getSpottedsByUserId(userId)

		if type(res) == list:
			return Response(json.dumps(res, cls=ObjectIdEncoder))

	return abort(400)

@app.route("/v1/contact", methods=['POST'])
def contact():
	form = ContactForm()
	if form.validate_on_submit():
		return "{}, {}".format(form.email.data, form.message.data)

	return abort(400)

