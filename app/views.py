#!/usr/bin/env python
import json

from functools import wraps

from app import app

from app.forms import ContactForm, CreateSpottedForm, GetSpottedsForm, RegisterFacebookIdForm, RegisterGoogleIdForm
from app.models import SpottedModel, UserModel
from app.utils import DecimalEncoder, validateUuid

from flask import abort, request

# Decorators
def requireAuthenticate(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth = request.authorization
		if auth:
			provider, token = auth.password.split('|')
			if validateUuid(auth.username) and provider in ['f','g']:
				user = UserModel().getUser(auth.username)
				if user:
					if provider == 'f':
						debugToken = UserModel().getDebugToken(token)
						if user['facebookId'] == debugToken['user_id']:
							return f(*args, **kwargs)
					elif provider == 'g':
						return f(*args, **kwargs)
		return abort(401)
	return decorated_function

@app.route("/v1/register/facebook", methods=['POST'])
def registerFacebook():
	form = RegisterFacebookIdForm()
	if form.validate_on_submit():
		if UserModel().registerFacebookIdToUserId(form.userId.data, form.facebookId.data):
			return "", 200
			
	return abort(400)

@app.route("/v1/register/google", methods=['POST'])
def registerGoogle():
	form = RegisterGoogleIdForm()
	if form.validate_on_submit():
		if UserModel().registerGoogleIdToUserId(form.userId.data, form.googleId.data):
			return "", 200
	
	return abort(400)

@app.route("/v1/spotted", defaults={'spottedId': None}, methods=['POST'])
def createSpotted():
	form = CreateSpottedForm()
	
	# Creates a spotted according to form data
	if form.validate_on_submit():
		userId = form.userId.data
		anonimity = form.anonimity.data
		longitude = form.longitude.data
		latitude = form.latitude.data
		message = form.message.data
		#picture = form.picture.data

		res = SpottedModel.createSpotted(userId=userId, anonimity=anonimity, latitude=latitude, longitude=longitude, message=message, picture=None)
		if res:
			return json.dumps({"spottedId": res}), 201
	
	return abort(400)

@app.route("/v1/spotted/<spottedId>", methods=['GET'])
def spotted(spottedId):
	# Returns a specific spotted
	if spottedId:
		if validateUuid(spottedId):
			res = SpottedModel.getSpottedBySpottedId(spottedId)
			if res:
				return json.dumps(res, cls=DecimalEncoder)

	return abort(400)

@app.route("/v1/spotteds", defaults={'userId': None}, methods=['GET'])
def spotteds():
	form = GetSpottedsForm(request.args)

	# Returns all corresponding spotteds according to arguments
	if form.validate():
		longitude = form.longitude.data
		latitude = form.latitude.data
		radius = form.radius.data
		locationOnly = form.locationOnly.data

		# If locationOnly is True, returns only the locations for all the spotteds.
		# Else, returns all spotteds with their whole data.
		res = SpottedModel.getSpotteds(latitude=latitude, longitude=longitude, radius=radius, locationOnly=locationOnly)
		if res:
			return json.dumps(res, cls=DecimalEncoder)

	return abort(400)

@app.route("/v1/spotteds/<userId>", methods=['GET'])
def spottedsByUserId(userId):
	# Returns all spotteds to a specific userId
	# NOTE : Make sure to only and only give this list if the user token correspond to the userId
	# 	Unless it only returns the NOT anonimous ones.
	if userId:
		if validateUuid(userId):
			res = SpottedModel.getSpottedsByUserId(userId)
			if res:
				return json.dumps(res, cls=DecimalEncoder)

	return abort(400)

@app.route("/v1/contact", methods=['POST'])
def contact():
	form = ContactForm()
	if form.validate_on_submit():
		return "{}, {}".format(form.email.data, form.message.data)

	return abort(400)

