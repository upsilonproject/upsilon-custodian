#!/usr/bin/python

import argparse
from upsilon import amqp, logger
import datetime
import MySQLdb

from MessageHandler import MessageHandler
from DatabaseConnection import DatabaseConnection
from RuntimeConfig import RuntimeConfig

import sys
import time

argParser = argparse.ArgumentParser();
args = argParser.parse_args()

config = RuntimeConfig(argParser.parse_args())

def on_timeout():
	global amqpConnection
	amqpConnection.close()


while True:
    print "Connecting to:", config.amqpHost
    try:
        amqpConnection = amqp.Connection(host = config.amqpHost, queue = config.amqpQueue)
        amqpConnection.setPingReply("upsilon-custodian", "development", "db, amqp")
        amqpConnection.startHeartbeater()
        amqpConnection.bind('upsilon.custodian.requests');
        amqpConnection.bind('upsilon.node.serviceresults');

        mysqlConnection = DatabaseConnection(MySQLdb.connect(user=config.dbUser, db = "upsilon", connect_timeout = 5))
        mysqlConnection.get("service", 1)

        messageHandler = MessageHandler(amqpConnection, mysqlConnection, config)
        amqpConnection.addMessageTypeHandler("GET_LIST", messageHandler.onGetList)
        amqpConnection.addMessageTypeHandler("GET_ITEM", messageHandler.onGetItem)
        amqpConnection.addMessageTypeHandler("HEARTBEAT", messageHandler.onHeartbeat)
        amqpConnection.addMessageTypeHandler("SERVICE_CHECK_RESULT", messageHandler.onServiceCheckResult)

        print "Connected, consuming"

        amqpConnection.startConsuming()

        time.sleep(5);
    except KeyboardInterrupt:
        print "Ctrl C"
        try:
            amqpConnection.close();
            mysqlConnection.conn.close();
        except Exception as e:
            print "exception in exception handler", str(e)

        sys.exit(0)
    except Exception as e: 
        print "Exception in connection", e 

logger.info("Exited?")
