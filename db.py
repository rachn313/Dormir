# database functions

import dbi
import sys
import pymysql
pymysql.install_as_MySQLdb()

def getConn(db):
    '''connect to the database'''
    conn = pymysql.connect(host='localhost',
                           user='root',
                           passwd='',
                           db=db,
                           charset='utf8mb4')
    curs = conn.cursor()
    conn.autocommit(True)
    return conn


# DSN = None

# def getConn(DB):
# 	global DSN
# 	if DSN is None:
# 		DSN = dbi.read_cnf()
# 	conn = dbi.connect(DSN)
# 	conn.select_db(DB)
# 	return conn

def getMyRooms(conn, uid):
	curs = dbi.dictCursor(conn)
	curs.execute('''select rmID, imgPath from Reviews where uid=%s''', [uid]) 
	return curs.fetchall() 
	''' get all the info for each post in the Reviews table'''


#insert everything but filename and return the pid of the inserted image
#FIX
def insertReview(conn, rmID, rating, review, imgPath):
    #add to post table
    curs = dbi.dictCursor(conn)
    curs.execute(
        '''insert into Reviews(rmID, rating, review, imgPath, time) 
        values (%s,%s,%s,%s, now())''',
        [rmID, rating, review, imgPath])
