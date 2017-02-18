#!/usr/bin/env python
import cgi

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, DecimalField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError

# Constants
MINIMUM_LONGITUDE = -180
MAXIMUM_LONGITUDE = 180

MINIMUM_LATITUDE = -90
MAXIMUM_LATITUDE = 90

MAXIMUM_CONTACT_MESSAGE_LENGTH = 1000
MAXIMUM_SPOTTED_MESSAGE_LENGTH = 5000

DEFAULT_LOCATION_ONLY = False

def escapeSpecialCharacters(form, field):
	field.data = cgi.escape(field.data, True)

def validateBoolean(form, field):
	if field.data.lower() == "true":
		field.data = True
	elif field.data.lower() == "false":
		field.data = False
	else:
		raise ValidationError("Anonymity must be true or false.")

class ContactForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	message = TextAreaField('Message', validators=[DataRequired(), Length(max=MAXIMUM_CONTACT_MESSAGE_LENGTH), escapeSpecialCharacters])

class CreateSpottedForm(FlaskForm):
	anonymity = StringField('anonymity', validators=[DataRequired(), validateBoolean])
	latitude = DecimalField('latitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	longitude = DecimalField('longitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	message = TextAreaField('message', validators=[DataRequired(), Length(max=MAXIMUM_SPOTTED_MESSAGE_LENGTH), escapeSpecialCharacters])
	picture = FileField('picture', validators=[FileAllowed(['jpg','png'])], default=None)

class GetSpottedsForm(FlaskForm):
	minLat = DecimalField('minLat', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	maxLat = DecimalField('maxLat', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	minLong = DecimalField('minLong', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	maxLong = DecimalField('maxLong', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	locationOnly = StringField('locationOnly', validators=[validateBoolean], default=DEFAULT_LOCATION_ONLY)

class MergeFacebookForm(FlaskForm):
	facebookId = StringField('facebookId', validators=[DataRequired(), escapeSpecialCharacters])
	token = StringField('token', validators=[DataRequired()])
	
class MergeGoogleForm(FlaskForm):
	googleId = StringField('googleId', validators=[DataRequired(), escapeSpecialCharacters])
	token = StringField('token', validators=[DataRequired()])

class LinkFacebookForm(FlaskForm):
	facebookId = StringField('facebookId', validators=[DataRequired(), escapeSpecialCharacters])
	token = StringField('token', validators=[DataRequired()])
	
class LinkGoogleForm(FlaskForm):
	googleId = StringField('googleId', validators=[DataRequired(), escapeSpecialCharacters])
	token = StringField('token', validators=[DataRequired()])
	
