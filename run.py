#!/usr/bin/env python
from os import path, environ
from sys import exit
from argparse import ArgumentParser

from app import app

if __name__=='__main__':
	parser = ArgumentParser(description="Nearby Flask server")

	parser.add_argument('--host', dest='host', default=None)
	parser.add_argument('--port', dest='port', default=None)
	parser.add_argument('-s', '--ssl', action='store_true', dest='ssl', default=False)

	args = parser.parse_args()
	
	if args.host:
		host = args.host
	else:
		host = app.config['HOST']

	if args.port:
		port = args.port
	else:
		port = app.config['PORT']

	if args.ssl or ('NEARBY_SETTINGS' in environ and environ['NEARBY_SETTINGS'] in ['prod', 'production']):
		if path.exists(path.join(path.dirname(__file__), "cert.pem")) and path.exists(path.join(path.dirname(__file__), "privkey.pem")):
			sslContext = ('cert.pem','privkey.pem')
			print("Certificates were found. SSL is enabled.")
		else:
			print("Certificates weren't found.")
			exit(0)
	else:
		sslContext = None

	# Start the app
	app.run(debug=app.config['DEBUG'],
		host=host,
		port=port,
		ssl_context=sslContext,
		use_reloader=False,
		threaded=True)


