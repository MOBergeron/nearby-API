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
