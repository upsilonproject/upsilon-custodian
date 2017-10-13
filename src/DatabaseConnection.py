import MySQLdb
from upsilon import logger

class DatabaseConnection():
    def __init__(self, conn):
        self.conn = conn;

    def get(self, itemType, itemQuery):
        try: 
            res = {
                "service": self.getService,
                "node": self.getNode
            }

            return res[itemType](itemQuery)
        except KeyError:
            return []

    def list(self, itemType):
        try: 
            res = {
                "service": self.getServiceList,
                "node": self.getNodeList
            }

            return res[itemType](itemQuery)
        except KeyError:
            return []

    def execute(self, query, args = []):
        logger.info("SQL:", query)
        logger.info("ARG:", args)

        cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        res = cursor.execute(query, args)

        rows = cursor.fetchall();
        
        cursor.close()

        logger.info("RES:", len(rows))
    
        return rows


    def getService(self, serviceId):
        query = "SELECT s.id AS serviceId, s.identifier FROM services s WHERE s.id = %s LIMIT 1"

        return self.execute(query, [serviceId]) 

    def getNode(self, nodeId):
        return self.execute("SELECT n.id AS nodeId, n.identifier, n.serviceType, n.lastUpdated, n.instanceApplicationVersion FROM nodes n WHERE n.id = %s LIMIT 1", [nodeId])


    def getServiceList(self):
        query = "SELECT s.id AS id, s.identifier, s.status FROM services s"

        return self.execute(query)

    def getNodeList(self):
        query = "SELECT n.id AS nodeId, n.identifier, n.serviceType, n.instanceApplicationVersion FROM nodes n "

        return self.execute(query)

    def addHeartbeat(self, hb):
        query = "INSERT INTO nodes (identifier, serviceType, lastUpdated) VALUES (%s, %s, utc_timestamp()) ON DUPLICATE KEY UPDATE lastUpdated = utc_timestamp(), serviceCount = %s, serviceType = %s, configs = %s, instanceApplicationVersion = %s "

        params = [
            hb.identifier, 
            hb.serviceType,
            hb.serviceCount,
            hb.serviceType,
            hb.configs,
            hb.instanceApplicationVersion
        ]

        return self.execute(query, params);

    def addServiceCheckResult(self, scr):
        query = "INSERT INTO services (identifier, node, description, executable, karma) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE karma = %s, output = %s, commandLine = %s, lastUpdated = %s, consecutiveCount = %s, lastChanged = %s, estimatedNextCheck = %s, isLocal = %s, node = %s, commandIdentifier = %s "

        self.execute(query, [
            scr.identifier, 
            scr.nodeIdentifier, 
            scr.description,
            scr.executable,
            scr.getKarma(),
            scr.getKarma(),
            scr.body,
            scr.commandLine,
            scr.lastUpdated,
            scr.consequtiveCount,
            scr.lastChanged,
            scr.estimatedNextCheck,
            scr.isLocal,
            scr.nodeIdentifier,
            scr.commandIdentifier
        ])

        query = "INSERT INTO service_check_results (node, service, karma, output, checked) VALUES (%s, %s, %s, %s, utc_timestamp()) "

        return self.execute(query, [
            scr.nodeIdentifier,
            scr.identifier,
            scr.karma,
            scr.body
        ])

