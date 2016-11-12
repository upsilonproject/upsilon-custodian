#!/usr/bin/python

import argparse
import ConfigParser
import pika
import MySQLdb
from upsilon import amqp

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

	def get(self, itemType, itemQuery):
		try: 
			res = {
				"service": self.getService,
                                "node": self.getNode
			}

			return res[itemType](itemQuery)
		except KeyError:
			return []

	def execute(self, query, args):
                print "SQL:", query
                print "ARG:", args

		cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

		res = cursor.execute(query, args)

		rows = cursor.fetchall();
		
		cursor.close()

                print "RES:", len(rows)
	
		return rows


	def getService(self, serviceId):
		query = "SELECT s.id AS serviceId, s.identifier FROM services s WHERE s.id = %s LIMIT 1"

                return self.execute(query, [serviceId]) 

	def getNode(self, nodeId):
		return self.execute("SELECT n.id AS nodeId, n.identifier, n.serviceType, n.lastUpdated, n.instanceApplicationVersion FROM nodes n WHERE n.id = %s LIMIT 1", [nodeId])


class MessageHandler():
	amqp = None
	mysql = None

	def __init__(self, amqpConnection, mysqlConnection):
		self.amqp = amqpConnection
		self.database = mysqlConnection

	def onGetList(self, channel, method, properties, body):
            print "Got message", method, properties, body

            channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

        def onGetItem(self, channel, method, properties, body):
            global config 

            print "Got message", method, properties, body

            itemType = properties.headers["itemType"]
            itemQuery = properties.headers["itemQuery"]

            databaseResult = self.database.get(itemType, itemQuery);

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

            channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

def on_timeout():
	global amqpConnection
	amqpConnection.close()


print "connecting to:", config.amqpHost
amqpConnection = amqp.Connection(host = config.amqpHost, queue = config.amqpQueue)
amqpConnection.setPingReply("custodian", "development", "db, amqp")
amqpConnection.bind('upsilon.custodian.requests');

mysqlConnection = DatabaseConnection(MySQLdb.connect(user=config.dbUser, db = "upsilon"))
mysqlConnection.get("service", 1)

messageHandler = MessageHandler(amqpConnection, mysqlConnection)
amqpConnection.addMessageTypeHandler("GET_LIST", messageHandler.onGetList)
amqpConnection.addMessageTypeHandler("GET_ITEM", messageHandler.onGetItem)

try:
	amqpConnection.startConsuming()
except KeyboardInterrupt:
	pass
