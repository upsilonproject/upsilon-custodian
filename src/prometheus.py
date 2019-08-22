from upsilon import logger
from prometheus_client import start_http_server, Summary
import random
import time
import threading

REQUEST_TIME = Summary("foo", "This is a description")

@REQUEST_TIME.time()
def process_request(t):
    time.sleep(t)

def startProm(port):
    logger.info("Starting Prometheus endpoint on " + str(port))
    start_http_server(port)
#    promThread = threading.Thread(target = start_http_server, args = (port))
#    promThread.start()
