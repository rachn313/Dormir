# database functions

import dbi
import sys
import pymysql
pymysql.install_as_MySQLdb()

DSN = None

def getConn(DB):
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    conn = dbi.connect(DSN)
    conn.select_db(DB)
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
	curs.execute('''select rmID from Reviews where uid=%s''', [uid]) 
	return curs.fetchall() 
	''' get all the info for each post in the Reviews table'''


#insert everything but filename and return the pid of the inserted image
#FIX
def insertReview(conn, uid, rmID, rating, review, imgPath):
    #add to post table
    curs = dbi.dictCursor(conn)
    curs.execute(
        '''insert into Reviews(uid, rmID, rating, review, imgPath, time) 
        values (%s, %s,%s,%s,%s, now())''',
        [uid, rmID, rating, review, imgPath])

def getSearchedRooms(conn, rmID):
	curs = dbi.dictCursor(conn)
	query = rmID
	if len(rmID) <= 3:
		query += "%"

	curs.execute('''select distinct rmID from Reviews where rmID like %s ''', [query])
	return curs.fetchall() 

def getRoomInfo(conn, rmID):
  curs = dbi.dictCursor(conn)
  curs.execute(''' select * from Reviews where rmID = %s''', [rmID])
  return curs.fetchall()

def getAverageRating(conn, rmID):
  curs = dbi.dictCursor(conn)
  curs.execute(''' select avg(rating) as rate from Reviews where rmID = %s group by rmID''', [rmID])
  return curs.fetchone()
