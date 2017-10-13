class ServiceCheckResult():
    nodeIdentifier = ""
    identifier = ""
    karma = ""
    body = ""
    description = ""
    executable = ""
    commandLine = ""
    lastUpdated = ""
    consequtiveCount = 0,
    lastChanged = ""
    estimatedNextCheck = ""
    isLocal = True,
    commandIdentifier = ""

    def getKarma(self):
        return "UNKNOWN"

class Heartbeat():
    identifier = ""
    serviceType = ""
    serviceCount = 0
    configs = ""
    instanceApplicationVersion = ""
