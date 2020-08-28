# database functions

import dbi

DSN = None

def init_db():
    db = get_db()
    with current_app.open_resource('tables.sql') as f:
        db.executescript(f.read().decode('utf8'))


    if db is not None:
        db.close()

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

def getUsername(conn, uid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select username from Users where uid = %s''', [uid])
    result = curs.fetchone()
    return result['username']

def getUidwithRmID(conn, rmID):
    curs = dbi.dictCursor(conn)
    curs.execute('''select uid from Reviews where rmID = %s''', [rmID])
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

#is there a review in the db
def existsReview(conn):
    curs = dbi.cursor(conn)
    curs.execute('''select * from Reviews''')
    return True if curs.fetchone() else False

#check if the review exists
def checkReview(conn, uid,rmID):
    curs = dbi.cursor(conn)
    curs.execute('''select * from Reviews where rmID=%s and uid=%s''', [rmID, uid])
    return True if curs.fetchone() else False

#insert everything but filename and return the pid of the inserted image
def insertReview(conn, uid, rmID, rating, review, imgPath):
    #add to post table
    curs = dbi.dictCursor(conn)
    try:
        curs.execute(
            '''insert into Reviews(uid, rmID, rating, review, imgPath, time) 
            values (%s,%s,%s,%s,%s, now())''',
            [uid, rmID, rating, review, imgPath])
    except Exception as err:
        #print(repr(err))
        return None
   

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
  return curs.fetchall()

def getAverageRating(conn, rmID):
  curs = dbi.dictCursor(conn)
  curs.execute('''select avg(rating) as rate from Reviews where rmID = %s group by rmID''', [rmID])
  return curs.fetchone()

def getallRooms(conn):
    curs = dbi.dictCursor(conn)
    curs.execute(''' select rmID from Reviews ''')
    return curs.fetchall()

def getMyRooms(conn, uid):
	curs = dbi.dictCursor(conn)
	curs.execute('''select * from Reviews where uid=%s''', [uid]) 
	return curs.fetchall()

def save_trueFalse(conn, rmID, uid):
    '''Are you following this profile? Returns true or false'''
    curs = dbi.cursor(conn)
    curs.execute('''select * from Saves where rmID=%s and uid=%s''', [rmID, uid])
    return True if curs.fetchone() else False

def addSave(conn, rmID, uid): 
    '''adds a like to the post into the Likes table'''
    curs = dbi.dictCursor(conn)
    try:
        curs.execute('''INSERT INTO Saves(rmID, uid)
                                VALUES(%s, %s)''', [rmID, uid])
    except Exception as err:
        #print(repr(err))
        return None
                                
def removeSave(conn, rmID, uid):
    '''removes a like to the post from the Likes table ''' 
    curs = dbi.dictCursor(conn)
    curs.execute('''DELETE from Saves where rmID=%s and uid=%s''', [rmID, uid])

def getSaved(conn, uid):
    '''' get all starred rooms for user'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT * FROM Saves WHERE uid = %s''', [uid])
    return curs.fetchall()

# edit a review by its uid 
def editReview(conn, uid, rmID, rating, review):
    curs = dbi.dictCursor(conn)
    curs.execute('''update Reviews set rating=%s, review=%s where uid=%s and rmID=%s''', 
                        [rating, review, uid, rmID])

def deleteReview(conn, uid, rmID):
    curs = dbi.dictCursor(conn)
    curs.execute('''delete from Reviews where uid = %s and rmID = %s''', [uid, rmID])

def changePfp(conn, uid, path):
    curs = dbi.dictCursor(conn)
    curs.execute('''update Users set profpicPath=%s where uid = %s''', [path, uid])

def getPicPath(conn, uid):
    curs = dbi.dictCursor(conn)
    curs.execute(''' select profpicPath from Users where uid = %s''', [uid])
    return curs.fetchone()

def randomReviewoftheDay(conn):
    curs = dbi.dictCursor(conn)
    curs.execute('''select rmID from Reviews order by rand() limit 1''')
    return curs.fetchone()

def getImgfromRmID(conn, rmID):
    curs = dbi.dictCursor(conn)
    curs.execute('''select imgPath from Reviews where rmID=%s and imgPath!="NA";''', [rmID])
    return curs.fetchone()


