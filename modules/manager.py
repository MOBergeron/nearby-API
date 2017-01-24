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
		if environment.lower() in self.DEVELOPMENT_NAME_LIST:
			app.config.from_object("app.config.DevelopmentConfiguration")
		elif environment.lower() in self.PRODUCTION_NAME_LIST:
			app.config.from_object("app.config.ProductionConfiguration")
		else:
			raise InvalidCommand("Option environment is incompatible with the accepted values. Accepted : ['development','production']")

		app.run(debug=app.config['DEBUG'],
			host=app.config['HOST'],
			port=app.config['PORT'],
			use_reloader=False,
			threaded=True)

manager.add_command("runserver", Server())