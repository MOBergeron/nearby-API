#!/usr/bin/env python
import json

from app import app

from app.forms import ContactForm, CreateSpottedForm, GetSpottedsForm

from flask import abort, request

@app.route("/v1/login", methods=['POST'])
def login():
	return "Login"

@app.route("/v1/register", methods=['POST'])
def register():
	return "Register"

@app.route("/v1/spotted", defaults={'spottedId': None}, methods=['GET', 'POST'])
@app.route("/v1/spotted/<spottedId>", methods=['GET'])
def spotted(spottedId):
	# Returns a specific spotted
	if spottedId:
		return spottedId

	# Creates a spotted according to form data
	form = CreateSpottedForm()
	if form.validate_on_submit():
		userId = form.userId.data
		anonimity = form.anonimity.data
		spottedDate = form.spottedDate.data
		longitude = form.longitude.data
		latitude = form.latitude.data
		message = form.message.data
		#picture = form.picture.data

		return json.dumps(request.form), 201

	return abort(400)

@app.route("/v1/spotteds", defaults={'userId': None}, methods=['GET'])
@app.route("/v1/spotteds/<userId>", methods=['GET'])
def spotteds(userId):
	# Returns all spotteds to a specific userId
	# NOTE : Make sure to only and only give this list if the user token correspond to the userId
	# 	Unless it only returns the NOT anonimous ones.
	if userId:
		return userId

	# Returns all corresponding spotteds according to arguments
	form = GetSpottedsForm(request.args)
	if form.validate():
		longitude = form.longitude.data
		latitude = form.latitude.data
		radius = form.radius.data
		locationOnly = form.locationOnly.data

		# If locationOnly is True, returns only the locations for all the spotteds.
		# Else, returns all spotteds with their whole data.

		return "{}, {}, {}, {}".format(longitude, latitude, radius, locationOnly)

	return abort(400)

@app.route("/v1/contact", methods=['POST'])
def contact():
	form = ContactForm()
	if form.validate_on_submit():
		return "{}, {}".format(form.email.data, form.message.data)

	return abort(400)

