#!/usr/bin/env python
import os

from app import app

if __name__=='__main__':
	if os.path.exists(os.path.join(os.path.basename(__file__), "cert.pem")) and os.path.exists(os.path.join(os.path.basename(__file__), "privkey.pem")):
		sslContext = ('cert.pem','privkey.pem')
		print("Certificates found. SSL is enabled.")
	else:
		sslContext = None

	# Start the app
	app.run(debug=app.config['DEBUG'],
		host=app.config['HOST'],
		port=app.config['PORT'],
		ssl_context=sslContext,
		use_reloader=False,
		threaded=True)