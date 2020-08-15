# database functions

import dbi
<<<<<<< HEAD
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
	curs.execute('''select rmID from Reviews where uid=%s''', [uid]) 
	return curs.fetchall() 
	''' get all the info for each post in the Reviews table'''

=======

DSN = None

def getConn(DB):
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    conn = dbi.connect(DSN)
    conn.select_db(DB)
    return conn


# get uid of a user by username
def getUid(conn, username):
    '''get uid given a username '''
    curs = dbi.dictCursor(conn)
    curs.execute('''select uid from Users where username = %s''', [username])
    result = curs.fetchone()
    return result['uid']

# gets all reviews
def getAllReviews(conn):
    ''' get all the info for each post in the Reviews table'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from Reviews''') 
    return curs.fetchall() 


# gets all posts in the db sorted by rating
def getAllReviewsSortByRating(conn):
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from Reviews order by rating''') #fix this to do sort by ratings based on search query
    return curs.fetchall()

# get single review
def getSinglePost(conn, rid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select rmID, building, rating, review, imgPath, time
                     from Reviews inner join Users on Users.uid=Reviews.uid where Reviews.rid = %s''', [rid])
    return curs.fetchone()

# returns posts where query matches post room id, building, floor, username, name
#fix this to apply to our table 
def getQueryReview(conn, query):
    curs = dbi.dictCursor(conn)
    curs.execute('''(select * from Posts where pname like %s 
                            or restaurant like %s or location like %s)
                    union
                    (select Posts.* from Posts inner join 
                            (select pid from Tagpost inner join Tags 
                            on Tags.tid = Tagpost.tid where Tags.ttype = %s) as p 
                            on Posts.pid = p.pid)
                    union
                    (select Posts.* from Posts inner join (select uid from Users 
                            where username like %s or fullname like %s) as u
                            on Posts.uid = u.uid)''',
                ['%'+query+'%', '%'+query+'%', '%'+query+'%', query, 
                    '%'+query+'%', '%'+query+'%'])
    return curs.fetchall() # change to limit x offset y order by time

# returns posts where query matches post name, tag, restaurant, username, fullname
# sorted by rating
#FIX
def getQueryReviewSortByRating(conn, query):
    curs = dbi.dictCursor(conn)
    curs.execute('''(select * from Posts where pname like %s 
                            or restaurant like %s or location like %s)
                    union
                    (select Posts.* from Posts inner join 
                            (select pid from Tagpost inner join Tags 
                            on Tags.tid = Tagpost.tid where Tags.ttype = %s) as p 
                            on Posts.pid = p.pid)
                    union
                    (select Posts.* from Posts inner join (select uid from Users 
                            where username like %s or fullname like %s) as u
                            on Posts.uid = u.uid) order by rating''',
                ['%'+query+'%', '%'+query+'%', '%'+query+'%', query, 
                    '%'+query+'%', '%'+query+'%'])
    return curs.fetchall()

# delete a post in the db 
def deleteReview(conn, rid):
    curs = dbi.dictCursor(conn)
    curs.execute('''delete from Reviews where pid = %s''', [rid])

# edit a post by its pid. can edit pname, restaurant, review
#fix
def editReview(conn, pid, pname, restaurant, location, rating, price, review):
    curs = dbi.dictCursor(conn)
    curs.execute('''update Posts set pname = %s, restaurant = %s, location=%s,
                        rating=%s, price=%s, review=%s where pid = %s''', 
                        [pname, restaurant, location, rating, price, review, pid])
>>>>>>> b10eb52a57c9eb7e263cec73c2e6733dcd2fd1af

#insert everything but filename and return the pid of the inserted image
#FIX
def insertReview(conn, uid, rmID, rating, review, imgPath):
    #add to post table
    curs = dbi.dictCursor(conn)
    curs.execute(
        '''insert into Reviews(uid, rmID, rating, review, imgPath, time) 
<<<<<<< HEAD
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
=======
        values (%s,%s,%s,%s,%s, now())''',
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
  curs.execute('''select uid, username, profpicPath, rmID, rating, review, imgPath, time 
        from Reviews inner join Users using (uid) where rmID = %s ''', [rmID])
>>>>>>> b10eb52a57c9eb7e263cec73c2e6733dcd2fd1af
  return curs.fetchall()

def getAverageRating(conn, rmID):
  curs = dbi.dictCursor(conn)
  curs.execute(''' select avg(rating) as rate from Reviews where rmID = %s group by rmID''', [rmID])
<<<<<<< HEAD
  return curs.fetchone()
=======
  return curs.fetchone()

def getMyRooms(conn, uid):
	curs = dbi.dictCursor(conn)
	curs.execute('''select * from Reviews where uid=%s''', [uid]) 
	return curs.fetchall()

#def getUsersforRoom(conn, rmID):
   # curs = dbi.dictCursor(conn)
	#curs.execute('''select * from Users where uid=%s''', [uid]) 
	#return curs.fetchall()
#def getImgs(conn, rmID):
 #   curs = dbi.dictCursor(conn)
  #  curs.execute('''select imgPath from Reviews where rmID = %s''',[rmID])
>>>>>>> b10eb52a57c9eb7e263cec73c2e6733dcd2fd1af
