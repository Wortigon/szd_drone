import mysql.connector
import time


class MySQLBase():

    def __init__(self):
        self.cnx = None

    def connect(self, user, password, host, database):
        self.cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)

    def insert(self, query, params):
        cur = self.cnx.cursor()
        cur.execute(query, params)
        self.cnx.commit()
        cur.close()

    def select(self, query, params):
        cur = self.cnx.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        cur.close()
        return result

    def getLastIdCopterData(self):
        cur = self.cnx.cursor()
        cur.execute("SELECT MAX(id) FROM CopterData;")
        result = cur.fetchone()[0]
        cur.close()
        return result

    @staticmethod
    def getTime():
        return time.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def formatInsertString(s, attrList):
        return s.format(','.join(attrList), ','.join(['%s' for i in xrange(len(attrList))]))

    # def __del__(self):
    #     self.cnx.close()
