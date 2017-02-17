#!/usr/bin/env python
from os import environ

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, instance_relative_config=True)

# Load default configuration
app.config.from_object('config.default')

config = 'dev'

if 'NEARBY_SETTINGS' in environ:
	config = environ['NEARBY_SETTINGS'].lower()

if config in ['dev', 'devel', 'development']:
	app.config.from_object('config.development')

elif config in ['prod', 'production']:
	app.config.from_object('config.production')

# Load local configuration
app.config.from_pyfile('config.py', silent=True)

mongo = PyMongo(app)

from app import views