class ServiceCheckResult():
    nodeIdentifier = ""
    identifier = ""
    karma = ""
    body = ""
    description = ""
    executable = ""
    commandLine = ""
    consequtiveCount = 0,
    lastChanged = ""
    estimatedNextCheck = ""
    isLocal = True,
    commandIdentifier = ""

class Heartbeat():
    identifier = ""
    serviceType = ""
    serviceCount = 0
    configs = ""
    instanceApplicationVersion = ""
