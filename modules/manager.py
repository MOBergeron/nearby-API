#!/usr/bin/env python
from app import app

from flask_script import Command, Manager, Option

manager = Manager(app)

class InvalidCommand(Exception):
	pass

class Server(Command):

	DEVELOPMENT_NAME_LIST = ["dev", "devel", "develop", "development"]
	PRODUCTION_NAME_LIST = ["prod", "production"]
	ENVIRONMENT_OPTIONS = DEVELOPMENT_NAME_LIST.extend(PRODUCTION_NAME_LIST)


	DATABASE_LOCAL_NAME = "local"
	DATABASE_REMOTE_NAME = "remote"
	DATABASE_OPTIONS = [DATABASE_LOCAL_NAME, DATABASE_REMOTE_NAME]

	option_list = [
		Option('--environment','-e', dest='environment', default="dev"),
		Option('--database','-d', dest='database', default="local")
	]

	def run(self, environment, database):
		from app.connection import DynamoDBConnection
		# Load default configuration
		app.config.from_object('config.default')
		
		# DB_REGION_NAME is set in config.default
		DynamoDBConnection().setRegionName(app.config['DB_REGION_NAME'])

		# Load development or production configuration
		if environment.lower() in self.DEVELOPMENT_NAME_LIST:
			app.config.from_object('config.development')
			
			if database.lower() == self.DATABASE_LOCAL_NAME:
				# Set endpoint_url to local address and port
				app.config['DB_ENDPOINT_URL'] = "http://127.0.0.1:8000"
				DynamoDBConnection().setEndpointUrl(app.config['DB_ENDPOINT_URL'])

				# Start a thread that will start DynamoDB
				from threading import Thread
				t = Thread(target=self.startDynamoDB)
				t.start()

				# Create local tables
				DynamoDBConnection().createLocalTables()

			elif database.lower() == self.DATABASE_REMOTE_NAME:
				# Nothing to do here yet.
				pass

			else:
				raise InvalidCommand("Option database is incompatible with accepted values. Accepted values are : ['{}']".format("', '".join(self.DATABASE_OPTIONS)))

		elif environment.lower() in self.PRODUCTION_NAME_LIST:
			app.config.from_object('config.production')

		else:
			raise InvalidCommand("Option environment is incompatible with the accepted values. Accepted : ['{}']".format("', '".join(self.ENVIRONMENT_OPTIONS)))

		# Load local configuration
		app.config.from_pyfile('config.py')
		
		from app import views

		# Start the app
		app.run(debug=app.config['DEBUG'],
			host=app.config['HOST'],
			port=app.config['PORT'],
			use_reloader=False,
			threaded=True)

	def startDynamoDB(self):
		from subprocess import call

		command = 'java -Djava.library.path=./instance/dynamodb/DynamoDBLocal_lib -jar instance/dynamodb/DynamoDBLocal.jar -sharedDb -inMemory'
		call(command.split())

# Add commands to the manager
manager.add_command("runserver", Server())