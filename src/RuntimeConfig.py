import configargparse

global config

parser = configargparse.ArgParser(default_config_files=["/etc/upsilon-custodian/custodian.cfg"])
parser.add("--dbUser")
parser.add("--dbPass", default = "")
parser.add("--dbName")
parser.add("--dbHost")
parser.add("--amqpHost")
parser.add("--amqpExchange")
parser.add("--amqpQueue", default = "upsilon-custodian")
parser.add("--promPort", default = 1300);
parser.add("--promOnly", action = 'store_true')
config = parser.parse_args();

def getRuntimeConfig():
  return config
