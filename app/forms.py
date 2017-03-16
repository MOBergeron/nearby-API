#!/usr/bin/env python
import cgi

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, DateTimeField, DecimalField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

# Constants
MINIMUM_LONGITUDE = -180
MAXIMUM_LONGITUDE = 180

MINIMUM_LATITUDE = -90
MAXIMUM_LATITUDE = 90

MAXIMUM_SPOTTED_MESSAGE_LENGTH = 1000

DEFAULT_LOCATION_ONLY = False

def escapeSpecialCharacters(form, field):
	field.data = cgi.escape(field.data, True)

def validateBoolean(form, field):
	if not isinstance(field.data, bool):
		if field.data.lower() == "true":
			field.data = True
		elif field.data.lower() == "false":
			field.data = False
		else:
			raise ValidationError("Anonymity must be true or false.")

class CreateSpottedForm(FlaskForm):
	anonymity = StringField('anonymity', validators=[DataRequired(), validateBoolean])
	latitude = DecimalField('latitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LATITUDE, max=MAXIMUM_LATITUDE)])
	longitude = DecimalField('longitude', validators=[DataRequired(), NumberRange(min=MINIMUM_LONGITUDE, max=MAXIMUM_LONGITUDE)])
	message = TextAreaField('message', validators=[DataRequired(), Length(max=MAXIMUM_SPOTTED_MESSAGE_LENGTH), escapeSpecialCharacters])
	picture = FileField('picture', validators=[FileAllowed(['jpg','png'])], default=None)

class GetMySpottedsForm(FlaskForm):
	skip = IntegerField('skip', validators=[NumberRange(min=0)], default=0)
	since = DateTimeField('since', format='%Y-%m-%d %H:%M:%S', default=None)

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
	
