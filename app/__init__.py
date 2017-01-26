#!/usr/bin/env python
from flask import Flask

app = Flask(__name__, instance_relative_config=True)

# http://stackoverflow.com/q/6760685
class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]