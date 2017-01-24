#!/usr/bin/env python
import os

class Configuration(object):
	SECRET_KEY = os.urandom(128)
	SESSION_TYPE = "null"

	DEBUG = False

	WTF_CSRF_ENABLED = False
	WTF_CSRF_SECRET_KEY = "WIw0%gxynPY1T5tZlNIz%K@PjqGw#h7rMu1Vw7Jy3u0xpVRNsBEByT!YC5EoVopzES!%npWDsDry49E!R!C*BdwB3pwQtnR^rHRn"

	# TODO: Add database info (creds, etc.)

class DevelopmentConfiguration(Configuration):
	DEBUG = True
	HOST = "127.0.0.1"
	PORT = 5000

class ProductionConfiguration(Configuration):
	HOST = "0.0.0.0"
	# TODO: Change the port to 443 when we'll be using SSL.
	PORT = 80 

