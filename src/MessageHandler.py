import json
import yaml
import pika
from upsilon import logger
from structures import ServiceCheckResult, Heartbeat

from prometheus_client import Counter

METRIC_MSG_SERVICE_CHECK_RESULT_COUNT = Counter('custodian_msg_service_check_result_count', '')
METRIC_MSG_GET_LIST_COUNT = Counter('custodian_msg_get_list_count', '')
METRIC_MSG_GET_ITEM_COUNT = Counter('custodian_msg_get_item_count', '')
METRIC_MSG_HEARTBEAT_COUNT = Counter('custodian_msg_heartbeat_count', '')

class MessageHandler():
    amqp = None
    mysql = None
    config = None

    def __init__(self, amqpConnection, mysqlConnection, config):
        self.amqp = amqpConnection
        self.database = mysqlConnection
        self.config = config

    def onGetList(self, channel, method, properties, body):
        logger.info("Got message", method, properties, body)

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

        logger.info("responding:", itemBody)

        METRIC_MSG_GET_LIST_COUNT.inc();

    def onGetItem(self, channel, method, properties, body):
        logger.info("Got message: ", method, properties, body)

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

        logger.info("responding: ", itemBody)

        channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

        METRIC_MSG_GET_ITEM_COUNT.inc();

    def onHeartbeat(self, channel, method, properties, body):
        hb = Heartbeat()
        hb.identifier = properties.headers['node-identifier']
        nodeType = "?"
        nodeTraits = "?"

        if "node-type" in properties.headers:
            nodeType = properties.headers["node-type"]

        if "node-traits" in properties.headers:
            nodeTraits = properties.headers["node-traits"]

        hb.serviceType = nodeType + "(" + nodeTraits + ")"

        if "node-configs" in properties.headers:
            hb.configs = properties.headers['node-configs']

        if "node-version" in properties.headers:
            hb.instanceApplicationVersion = properties.headers['node-version']

        if "node-service-count" in properties.headers:
            hb.serviceCount = properties.headers['node-service-count']

        self.database.addHeartbeat(hb)

        channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

        METRIC_MSG_HEARTBEAT_COUNT.inc();

    def onServiceCheckResult(self, channel, method, properties, body):
        serviceCheckResult = ServiceCheckResult()
        serviceCheckResult.nodeIdentifier = properties.headers["node-identifier"]
        serviceCheckResult.identifier = properties.headers["identifier"]
        serviceCheckResult.karma = properties.headers["karma"]
        serviceCheckResult.body = str(body)

        self.database.addServiceCheckResult(serviceCheckResult)
        
        channel.basic_ack(delivery_tag = method.delivery_tag, multiple = False)

        METRIC_MSG_SERVICE_CHECK_RESULT_COUNT.inc();

    def dumpDefault(self, obj):
            if type(obj) == datetime.datetime:
                return str(obj)

            return str(obj)


