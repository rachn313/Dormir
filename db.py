# database functions

import dbi

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

#insert everything but filename and return the pid of the inserted image
#FIX
def insertReview(conn, uid, rmID, rating, review, imgPath):
    #add to post table
    curs = dbi.dictCursor(conn)
    curs.execute(
        '''insert into Reviews(uid, rmID, rating, review, imgPath, time) 
        values (%s,%s,%s,%s,%s, now())''',
        [uid, rmID, rating, review, imgPath])
   

#inserts the image path named with the pid
#FIX
def insertFilepath(conn, path, pid):
    curs = dbi.dictCursor(conn)
    curs.execute('''update Posts set imgPath = %s where pid = %s''',[path, pid])