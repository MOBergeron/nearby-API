#!/usr/bin/env python
import os

DEBUG = False
WTF_CSRF_ENABLED = False

SESSION_TYPE = "null"
DB_REGION_NAME = "us-east-1"
DB_ENDPOINT_URL = None

INSTANCE_FOLDER_NAME = "instance"
DYNAMODB_FOLDER_NAME = "dynamodb"
DYNAMODB_PATH = os.path.join(INSTANCE_FOLDER_NAME, DYNAMODB_FOLDER_NAME)

FACEBOOK_API = "https://graph.facebook.com"
FACEBOOK_DEBUG_URL = FACEBOOK_API + "/debug_token?input_token={input_token}&access_token={access_token}"
