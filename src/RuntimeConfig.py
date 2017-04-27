import ConfigParser

configParser = ConfigParser.ConfigParser()
configParser.readfp(open('/etc/upsilon-custodian/defaults.cfg'))

class RuntimeConfig:
	dbUser = configParser.get('database', 'user')
	dbPass = configParser.get('database', 'pass')

	amqpHost = configParser.get('amqp', 'host')
	amqpExchange = configParser.get('amqp', 'exchange');
	amqpQueue = configParser.get('amqp', 'queue');

	def __init__(self, args):
		self.args = args

