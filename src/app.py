#!/usr/bin/python

import argparse
import ConfigParser
import pika
import MySQLdb

import yaml
import json

argParser = argparse.ArgumentParser();
args = argParser.parse_args()

configParser = ConfigParser.ConfigParser()
configParser.readfp(open('/etc/upsilon-custodian/defaults.cfg'))

class RuntimeConfig:
	dbUser = configParser.get('database', 'user')
	dbPass = configParser.get('database', 'pass')

	amqpHost = configParser.get('amqp', 'host')
	amqpExchange = configParser.get('amqp', 'exchange');
	amqpQueue = configParser.get('amqp', 'queue');

	def __init__(self):
		args = argParser.parse_args()

config = RuntimeConfig()


class DatabaseConnection():
	def __init__(self, conn):
		self.conn = conn;

	def get(self, itemType, itemId):
		try: 
			res = {
				"service": self.getService
			}

			res[itemType](itemId)
		except KeyError:
			return []

	def execute(self, query, args):
		cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

		res = cursor.execute(query, args)

		rows = cursor.fetchall();
		
		cursor.close()
	
		return rows


	def getService(self, serviceId):
		cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
		query = "SELECT s.id AS serviceId, s.identifier FROM services s WHERE s.id = %s LIMIT 1"

		res = cursor.execute(query, serviceId)

		rows = cursor.fetchall();
		
		cursor.close()
	
		return rows


	def getNode(self, nodeId):
		return self.execute("SELECT s.name AS nodeId, n.name FROM nodes n WHERE n.id = %s LIMIT 1", itemId)


class MessageHandler():
	amqp = None
	mysql = None

	def __init__(self, amqpConnection, mysqlConnection):
		self.amqp = amqpConnection
		self.database = mysqlConnection

	def onMessage(self, channel, method, properties, body):
		global config 
		print properties.headers
		msgType = properties.headers['upsilon-msg-type']

		if msgType == "GET_ITEM":
			print "Got message", method, properties, body

			itemType = properties.headers["itemType"]
			itemId = properties.headers["itemId"]

			databaseResult = self.database.get(itemType, itemId);

			headers = {}
			headers['upsilon-msg-type'] = 'GET_ITEM_RESULT'

			if databaseResult == None or len(databaseResult) == 0:
				headers['status'] = 'not-found'
				itemBody = "not found"
			else:
				headers['status'] = 'found'

				if not "result-format" in properties.headers or properties.headers['result-format'] == "json" or properties.headers['result-format'] == "":
					itemBody = json.dumps(databaseResult, indent = 4)
				elif properties.headers['result-format'] == 'yaml':
					itemBody = yaml.dump(databaseResult)
				else:
					headers['status'] = 'unsupported-format'

					itemBody = "UNSUPPORTED FORMAT"

			channel.basic_publish(exchange = config.amqpExchange, routing_key = 'upsilon.custodian.results', properties = pika.BasicProperties(
				reply_to = str(method.delivery_tag),
				headers = headers
			), body = itemBody)

			print "responding: ", itemBody

		elif msgType == "GET_LIST":
			print "Got message", method, properties, body
		else: 
			print "UNSUPPORTED MESSAGE", msgType

		channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

def on_timeout():
	global amqpConnection
	amqpConnection.close()


print config.amqpHost
amqpConnection = pika.BlockingConnection(pika.ConnectionParameters(host = config.amqpHost))
print amqpConnection.is_open
 
channel = amqpConnection.channel();
channel.queue_declare(queue = config.amqpQueue, durable = False, auto_delete = True)
channel.queue_bind(queue = config.amqpQueue, exchange = config.amqpExchange, routing_key = 'upsilon.custodian.requests');

mysqlConnection = DatabaseConnection(MySQLdb.connect(user=config.dbUser, db = "upsilon"))
mysqlConnection.get("service", 1)

messageHandler = MessageHandler(amqpConnection, mysqlConnection)

channel.basic_consume(messageHandler.onMessage, queue = config.amqpQueue)

try:
	channel.start_consuming()
except KeyboardInterrupt:
	pass
