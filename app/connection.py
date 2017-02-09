#!/usr/bin/env python
import boto3

from app.utils import Singleton

class DynamoDBConnection(object):
	__metaclass__ = Singleton

	def __init__(self):
		self.__dynamodb = None
		self.__spottedTable = None
		self.__userTable = None
		self.__region_name = None
		self.__endpoint_url = None

	def createLocalTables(self):
		self.__getDynamoDBObject().create_table(
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
				},
				{
					'AttributeName': 'facebookId',
					'AttributeType': 'S'
				},
				{
					'AttributeName': 'googleId',
					'AttributeType': 'S'
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 10,
				'WriteCapacityUnits': 10
			},
			GlobalSecondaryIndexes=[
				{
					'IndexName': 'facebookIdIndex',
					'KeySchema': [
						{
							'AttributeName': 'facebookId',
							'KeyType': 'HASH',
						},
					],
					'Projection': {
						'ProjectionType': 'ALL',
					},
					'ProvisionedThroughput': {
						'ReadCapacityUnits': 2,
						'WriteCapacityUnits': 2,
					}
				},
				{
					'IndexName': 'googleIdIndex',
					'KeySchema': [
						{
							'AttributeName': 'googleId',
							'KeyType': 'HASH',
						},
					],
					'Projection': {
						'ProjectionType': 'ALL',
					},
					'ProvisionedThroughput': {
						'ReadCapacityUnits': 2,
						'WriteCapacityUnits': 2,
					}
				}
			]
		)

		self.__getDynamoDBObject().create_table(
			TableName='spotted',
			KeySchema=[
				{
					'AttributeName': 'spottedId',
					'KeyType': 'HASH'
				},
			],
			AttributeDefinitions=[
				{
					'AttributeName': 'spottedId',
					'AttributeType': 'S'
				},
				{
					'AttributeName': 'userId',
					'AttributeType': 'S'
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 10,
				'WriteCapacityUnits': 10
			},
			GlobalSecondaryIndexes=[
				{
					'IndexName': 'userIdIndex',
					'KeySchema': [
						{
							'AttributeName': 'userId',
							'KeyType': 'HASH',
						},
					],
					'Projection': {
						'ProjectionType': 'ALL',
					},
					'ProvisionedThroughput': {
						'ReadCapacityUnits': 2,
						'WriteCapacityUnits': 2,
					}
				}
			],
		)
		print("Local tables are created.")

	def __getDynamoDBObject(self):
		if self.__dynamodb is None:
			self.__dynamodb = boto3.resource('dynamodb', region_name=self.__region_name, endpoint_url=self.__endpoint_url)
		return self.__dynamodb

	def getSpottedTable(self):
		if self.__spottedTable is None:
			self.__spottedTable = self.__getDynamoDBObject().Table("spotted")
		return self.__spottedTable

	def getUserTable(self):
		if self.__userTable is None:
			self.__userTable = self.__getDynamoDBObject().Table("user")
		return self.__userTable

	def setRegionName(self, region_name):
		self.__region_name = region_name

	def setEndpointUrl(self, endpoint_url):
		self.__endpoint_url = endpoint_url