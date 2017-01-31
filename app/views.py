#!/usr/bin/env python
import json

from app import app

from app.forms import ContactForm, CreateSpottedForm, GetSpottedsForm
from app.models import SpottedModel, UserModel
from app.utils import DecimalEncoder, validateUuid

from flask import abort, request

@app.route("/v1/login", methods=['POST'])
def login():
	UserModel().validateFacebookToken(app.config['FACEBOOK_DEBUG_URL'], "TOKEN", app.config['FACEBOOK_ACCESS_TOKEN'])
	return "Login"

@app.route("/v1/register", methods=['POST'])
def register():
	return "Register"

@app.route("/v1/spotted", defaults={'spottedId': None}, methods=['GET', 'POST'])
@app.route("/v1/spotted/<spottedId>", methods=['GET'])
def spotted(spottedId):
	form = CreateSpottedForm()
	
	# Returns a specific spotted
	if spottedId:
		if validateUuid(spottedId):
			res = SpottedModel.getSpottedBySpottedId(spottedId)
			if res:
				return json.dumps(res, cls=DecimalEncoder)

	# Creates a spotted according to form data
	elif form.validate_on_submit():
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

@app.route("/v1/spotteds", defaults={'userId': None}, methods=['GET'])
@app.route("/v1/spotteds/<userId>", methods=['GET'])
def spotteds(userId):
	form = GetSpottedsForm(request.args)
	# Returns all spotteds to a specific userId
	# NOTE : Make sure to only and only give this list if the user token correspond to the userId
	# 	Unless it only returns the NOT anonimous ones.
	if userId:
		if validateUuid(userId):
			res = SpottedModel.getSpottedsByUserId(userId)
			if res:
				return json.dumps(res, cls=DecimalEncoder)

	# Returns all corresponding spotteds according to arguments
	elif form.validate():
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

@app.route("/v1/contact", methods=['POST'])
def contact():
	form = ContactForm()
	if form.validate_on_submit():
		return "{}, {}".format(form.email.data, form.message.data)

	return abort(400)

