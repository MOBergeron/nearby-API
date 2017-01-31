#!/usr/bin/env python
import os

from app import app

from flask_script import Command, Manager, Option

manager = Manager(app)

class InvalidCommand(Exception):
	pass

class Install(Command):
	def run(self):
		import pip
		import urllib2
		from zipfile import ZipFile
		from StringIO import StringIO
		
		dynamodbPath = app.config['DYNAMODB_PATH']

		print("Checking if '{}' directory exists...".format(dynamodbPath))
		if not os.path.exists(dynamodbPath):
			print("Creating '{}' directory...".format(dynamodbPath))
			os.makedirs(dynamodbPath)

		print("Downloading DynamoDB, this may take a while...")
		downloadedZipFile = urllib2.urlopen("https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.zip").read()
		zipFile = ZipFile(StringIO(downloadedZipFile))
		print("Unzipping DynamoDB, to '{}' path...".format(dynamodbPath))

		for fileName in zipFile.namelist():
			destination = os.path.join(dynamodbPath, fileName)

			if fileName.endswith('/'):
				print("Creating '{}' folder...".format(destination))
				os.makedirs(destination)
			else:
				print("Creating '{}'...".format(destination))
				with open(destination, 'w') as f:	
					f.write(zipFile.read(fileName))
		zipFile.close()
		print("Unzipping is done.")

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

		command = 'java -Djava.library.path=./{0}/DynamoDBLocal_lib -jar {0}/DynamoDBLocal.jar -sharedDb -inMemory'.format(app.config['DYNAMODB_PATH'])
		call(command.split())


# Add commands to the manager
manager.add_command("install", Install())
manager.add_command("runserver", Server())