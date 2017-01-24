#!/usr/bin/env python
import boto3

from app import app

dynamodb = boto3.resource('dynamodb', region_name=app.config['DB_REGION_NAME'], endpoint_url=app.config['DB_ENDPOINT_URL'])

