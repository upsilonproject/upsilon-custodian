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

    def execute(self, query, args):
        print "SQL:", query
        print "ARG:", args

        cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        res = cursor.execute(query, args)

        rows = cursor.fetchall();
        
        cursor.close()

        print "RES:", len(rows)
    
        return rows


    def getService(self, serviceId):
        query = "SELECT s.id AS serviceId, s.identifier FROM services s WHERE s.id = %s LIMIT 1"

        return self.execute(query, [serviceId]) 

    def getNode(self, nodeId):
        return self.execute("SELECT n.id AS nodeId, n.identifier, n.serviceType, n.lastUpdated, n.instanceApplicationVersion FROM nodes n WHERE n.id = %s LIMIT 1", [nodeId])


    def getNodeList(self):
        query = "SELECT n.id AS nodeId, n.identifier, n.serviceType, n.instanceApplicationVersion FROM nodes n "

        return self.execute(query, [])
