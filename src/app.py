#!/usr/bin/python

import argparse
import ConfigParser
import pika
import _mysql

argParser = argparse.ArgumentParser();
args = argParser.parse_args()

configParser = ConfigParser.ConfigParser()
configParser.readfp(open('defaults.cfg'))

class RuntimeConfig:
	dbUser = configParser.get('database', 'user')
	dbPass = configParser.get('database', 'pass')

	amqpHost = configParser.get('amqp', 'host')
	amqpExchange = configParser.get('amqp', 'exchange');
	amqpQueue = configParser.get('amqp', 'queue');

	def __init__(self):
		args = argParser.parse_args()

config = RuntimeConfig()

class MessageHandler():
	amqp = None
	mysql = None

	def __init__(self, amqpConnection, mysqlConnection):
		self.amqp = amqpConnection
		self.mysql = mysqlConnection

	def onMessage(self, channel, method, properties, body):
		global config 
		msgType = properties.headers['upsilon-msg-type']

		if msgType == "GET_ITEM":
			print "Got message", method, properties, body

			itemBody = "[]";

			channel.basic_publish(exchange = config.exchange, routing_key = 'upsilon.custodian.gets', properties = pika.BasicProperties(
				reply_to = method.delivery_tag
			), body = itemBody)

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
channel.queue_bind(queue = config.amqpQueue, exchange = config.amqpExchange, routing_key = 'upsilon.node.serviceresults');
channel.queue_bind(queue = config.amqpQueue, exchange = config.amqpExchange, routing_key = '#');
channel.queue_bind(queue = config.amqpQueue, exchange = config.amqpExchange, routing_key = '*');

mysqlConnection = _mysql.connect(user=config.dbUser)

messageHandler = MessageHandler(amqpConnection, mysqlConnection)

channel.basic_consume(messageHandler.onMessage, queue = config.amqpQueue)

try:
	channel.start_consuming()
except KeyboardInterrupt:
	pass
