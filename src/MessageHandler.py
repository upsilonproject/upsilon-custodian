import json
import yaml
import pika
from upsilon import logger

class MessageHandler():
    amqp = None
    mysql = None
    config = None

    def __init__(self, amqpConnection, mysqlConnection, config):
        self.amqp = amqpConnection
        self.database = mysqlConnection
        self.config = config

    def onGetList(self, channel, method, properties, body):
        print "Got message", method, properties, body

        itemType = properties.headers["itemType"]

        databaseResult = self.database.list(itemType);

        headers = {}
        headers['upsilon-msg-type'] = 'GET_LIST_RESULT'

        if len(databaseResult) == 0:
            itemBody = "not found"
        else:
            itemBody = json.dumps(databaseResult, indent = 4, default = self.dumpDefault)

        channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)
        channel.basic_publish(exchange = self.config.amqpExchange, routing_key = 'upsilon.custodian.results', properties = pika.BasicProperties(
                reply_to = str(method.delivery_tag),
                headers = headers
        ), body = itemBody)

        logger.info("responding: " + itemBody)

    def onGetItem(self, channel, method, properties, body):
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
                        itemBody = json.dumps(databaseResult, indent = 4, default=self.dumpDefault)
                elif properties.headers['result-format'] == 'yaml':
                        itemBody = yaml.dump(databaseResult)
                else:
                        headers['status'] = 'unsupported-format'

                        itemBody = "UNSUPPORTED FORMAT"

        channel.basic_publish(exchange = self.config.amqpExchange, routing_key = 'upsilon.custodian.results', properties = pika.BasicProperties(
                reply_to = str(method.delivery_tag),
                headers = headers
        ), body = itemBody)

        print "responding: ", itemBody

        channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

    def dumpDefault(self, obj):
            if type(obj) == datetime.datetime:
                return str(obj)

            return str(obj)


