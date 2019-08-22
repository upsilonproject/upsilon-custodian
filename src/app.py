#!/usr/bin/env python2

import argparse
from upsilon import amqp, logger
import datetime
import MySQLdb

from MessageHandler import MessageHandler
from DatabaseConnection import DatabaseConnection
from RuntimeConfig import getRuntimeConfig
from prometheus import startProm
from prometheus_client import Info

import sys
import time
from time import sleep

METRIC_PROM = Info('custodian_prom', 'Prometheus info')

argParser = argparse.ArgumentParser();
args = argParser.parse_args()

config = getRuntimeConfig()
METRIC_PROM.info({
    'port': str(config.promPort), 
    'only': str(config.promOnly)
})

def on_timeout():
	global amqpConnection
	amqpConnection.close()

def newAmqpConnection(config):
    logger.info("Connecting to:",  config.amqpHost, config.amqpQueue)

    amqpConnection = amqp.Connection(host = config.amqpHost, queue = config.amqpQueue)
    amqpConnection.setPingReply("upsilon-custodian", "development", "db, amqp")
    amqpConnection.startHeartbeater()
    amqpConnection.bind('upsilon.custodian.requests');
    amqpConnection.bind('upsilon.node.serviceresults');
    amqpConnection.bind('upsilon.node.heartbeats');


def startConnections():
    amqpConnection = newAmqpConnection(config);

    mysqlConnection = DatabaseConnection(MySQLdb.connect(host=config.dbHost, user=config.dbUser, passwd=config.dbPass, db = "upsilon", connect_timeout = 5, autocommit = True))

    messageHandler = MessageHandler(amqpConnection, mysqlConnection, config)
    amqpConnection.addMessageTypeHandler("GET_LIST", messageHandler.onGetList)
    amqpConnection.addMessageTypeHandler("GET_ITEM", messageHandler.onGetItem)
    amqpConnection.addMessageTypeHandler("HEARTBEAT", messageHandler.onHeartbeat)
    amqpConnection.addMessageTypeHandler("SERVICE_CHECK_RESULT", messageHandler.onServiceCheckResult)

    logger.info("AMQP and MySQL are connected, consuming")

    amqpConnection.startConsuming()


while True:
    try:
        startProm(config.promPort);

        if not config.promOnly:
            startConnections();

        time.sleep(5);
    except KeyboardInterrupt:
        logger.info("Ctrl C, will try and close connections")

        try:
            amqpConnection.close();
            mysqlConnection.conn.close();
        except Exception as e:
            logger.error("exception in exception handler: ", e)

        sys.exit(0)
    except Exception as e: 
        logger.error("Exception in connection: ", e)

        try: 
          amqpConnection.close()
        except:
          pass

        try:
          mysqlConnection.conn.close()
        except:
          pass


    sleep(20)

logger.info("Exited?")
