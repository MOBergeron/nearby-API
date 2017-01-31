#!/usr/bin/env python
import cgi

from app.utils import validateUuid

from flask_wtf import FlaskForm

from wtforms import BooleanField, DecimalField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError

# Constants
MINIMUM_LONGITUDE = -90
MAXIMUM_LONGITUDE = 90

MINIMUM_LATITUDE = -90
MAXIMUM_LATITUDE = 90

MINIMUM_RADIUS = 1
MAXIMUM_RADIUS = 100

MAXIMUM_CONTACT_MESSAGE_LENGTH = 1000
MAXIMUM_SPOTTED_MESSAGE_LENGTH = 5000

DEFAULT_LOCATION_ONLY = False

def escapeSpecialCharacters(form, field):
	field.data = cgi.escape(field.data, True)

def validateUuidField(form, field):
	if not validateUuid(field.data):
		raise ValidationError("UserID must be a valid UUID.")

class ContactForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	message = TextAreaField('Message', validators=[DataRequired(), Length(max=MAXIMUM_CONTACT_MESSAGE_LENGTH), escapeSpecialCharacters])

class CreateSpottedForm(FlaskForm):
	userId = StringField('userId', validators=[DataRequired(), validateUuidField, escapeSpecialCharacters])
	anonimity = BooleanField('anonimity', validators=[DataRequired()])
	longitude = DecimalField('longitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	latitude = DecimalField('latitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	message = TextAreaField('message', validators=[DataRequired(), Length(max=MAXIMUM_SPOTTED_MESSAGE_LENGTH), escapeSpecialCharacters])
	#picture = Field()

class GetSpottedsForm(FlaskForm):
	longitude = DecimalField('longitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	latitude = DecimalField('latitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	radius = IntegerField('radius', validators=[DataRequired(), NumberRange(min=MINIMUM_RADIUS, max=MAXIMUM_RADIUS)])
	locationOnly = BooleanField('locationOnly', default=DEFAULT_LOCATION_ONLY)