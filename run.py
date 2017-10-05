#!/usr/bin/env python
from os import path, environ
from sys import exit
from argparse import ArgumentParser

from app import app

if __name__=='__main__':
	parser = ArgumentParser(description="Nearby Flask server")

	parser.add_argument('--host', dest='host', default=None)
	parser.add_argument('--port', dest='port', default=None)

	args = parser.parse_args()
	
	if args.host:
		host = args.host
	else:
		host = app.config['HOST']

	if args.port:
		port = args.port
	else:
		port = app.config['PORT']

	if not 'AWS_ACCESS_KEY_ID' in environ or not 'AWS_SECRET_ACCESS_KEY' in environ:
		if 'AWS_ACCESS_KEY_ID' in app.config and 'AWS_SECRET_ACCESS_KEY' in app.config:
			environ['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
			environ['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']
		else:
			print("Missing AWS keys")
			exit(0)

	# Start the app
	app.run(debug=app.config['DEBUG'],
		host=host,
		port=port,
		use_reloader=False,
		threaded=True)


