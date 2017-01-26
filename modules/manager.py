#!/usr/bin/env python
from app import app

from flask_script import Command, Manager, Option

manager = Manager(app)

class InvalidCommand(Exception):
	pass

class Server(Command):

	DEVELOPMENT_NAME_LIST = ["dev", "devel", "develop", "development"]
	PRODUCTION_NAME_LIST = ["prod", "production"]

	option_list = [
		Option('--environment','-e', dest='environment', default="dev")
	]

	def run(self, environment):
		# Load default configuration
		app.config.from_object('config.default')

		# Load development or production configuration
		if environment.lower() in self.DEVELOPMENT_NAME_LIST:
			app.config.from_object('config.development')
		elif environment.lower() in self.PRODUCTION_NAME_LIST:
			app.config.from_object('config.production')
		else:
			raise InvalidCommand("Option environment is incompatible with the accepted values. Accepted : ['development','production']")

		# Load local configuration
		app.config.from_pyfile('config.py')

		# Initialize database connection, models and views
		from app import connection
		from app import models
		from app import views
		
		# Start the app
		app.run(debug=app.config['DEBUG'],
			host=app.config['HOST'],
			port=app.config['PORT'],
			use_reloader=False,
			threaded=True)

# Add commands to the manager
manager.add_command("runserver", Server())