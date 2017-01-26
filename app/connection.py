#!/usr/bin/env python
import boto3

from app import app
from app import Singleton

class DynamoDBConnection(object):
	__metaclass__ = Singleton

	def __init__(self):
		self.__spottedTable = None
		self.__userTable = None
		self.__dynamodb = boto3.resource('dynamodb', region_name=app.config['DB_REGION_NAME'], endpoint_url=app.config['DB_ENDPOINT_URL'])

		# Create default tables on development environment
		if app.config['ENVIRONMENT'] == "development":
			self.__spottedTable = self.__dynamodb.Table("spotted")

			try:
				self.__spottedTable.delete()
			except:
				pass
			
			self.__spottedTable = None
			self.__userTable = self.__dynamodb.Table("user")
			
			try:
				self.__userTable.delete()
			except:
				pass
			
			self.__userTable = None

			self.__dynamodb.create_table(
				TableName='user',
				KeySchema=[
					{
						'AttributeName': 'userId',
						'KeyType': 'HASH'
					}
				],
				AttributeDefinitions=[
					{
						'AttributeName': 'userId',
						'AttributeType': 'S'
					}

				],
				ProvisionedThroughput={
					'ReadCapacityUnits': 10,
					'WriteCapacityUnits': 10
				}
			)

			self.__dynamodb.create_table(
				TableName='spotted',
				KeySchema=[
					{
						'AttributeName': 'spottedId',
						'KeyType': 'HASH'
					}
				],
				AttributeDefinitions=[
					{
						'AttributeName': 'spottedId',
						'AttributeType': 'S'
					}

				],
				ProvisionedThroughput={
					'ReadCapacityUnits': 10,
					'WriteCapacityUnits': 10
				}
			)

	def getSpottedTable(self):
		if self.__spottedTable is None:
			self.__spottedTable = self.__dynamodb.Table("spotted")
		return self.__spottedTable

	def getUserTable(self):
		if self.__userTable is None:
			self.__userTable = self.__dynamodb.Table("user")
		return self.__userTable