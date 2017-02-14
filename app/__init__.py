#!/usr/bin/env python
from sys import argv

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, instance_relative_config=True)

# Load default configuration
app.config.from_object('config.default')
app.config.from_object('config.development')

mongo = PyMongo(app)

try:
	# Load local configuration
	app.config.from_pyfile('config.py')
except Exception as e:
	print(e.message)

from app import views

