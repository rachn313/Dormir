from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)



app = Flask(__name__)
app.secret_key = 'rosebud'  # so we can have sessions, which are necessary

import os
import dbi
import imghdr
import db 
import dbi # database stuff
import json

DB = 'dormir'

from flask_cas import CAS

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# the following doesn't work :-(
app.config['CAS_AFTER_LOGOUT'] = 'after_logout'


@app.route('/logged_in/')
def logged_in():
    flash('successfully logged in!')
    return redirect( url_for('index') )


@app.route('/after_logout/')
def after_logout():
    flash('successfully logged out!')
    return redirect( url_for('index') )

application = app


@app.route('/')
def index():
    # if "username" in session:
    #    return redirect(url_for("home"))
    # return render_template('home.html', page_title='Dormir')
    print('Session keys: ',list(session.keys()))
    for k in list(session.keys()):
        print(k,' => ',session[k])
    if '_CAS_TOKEN' in session:
        token = session['_CAS_TOKEN']
    if 'CAS_ATTRIBUTES' in session:
        attribs = session['CAS_ATTRIBUTES']
        print('CAS_attributes: ')
        for k in attribs:
            print('\t',k,' => ',attribs[k])
    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')
    return render_template('home.html',
                           username=username,
                           is_logged_in=is_logged_in,
                           cas_attributes = session.get('CAS_ATTRIBUTES'))


@app.route('/profile/')
def profile():
    # if "username" in session:
    #    return redirect(url_for("profile"))
    conn = db.getConn(DB)
    #uid = get it from session. 
    uid = 1 #temporary.
    rooms = db.getMyRooms(conn, uid)
    return render_template('profile.html', page_title='Dormir', my_rooms = rooms)   

@app.route('/upload/', methods=["POST"])
def upload(): 
    '''adds a post's information into the database'''
    roomCode = request.form.get("rCode")
    print(roomCode)
    roomNum = request.form.get("rNum")
    print(roomNum)
    rating = request.form.get("rating")
    print(rating)
    review = request.form.get("review")
    print(review)

    uid = 1 #MAKE SURE TO CHANGE!! 
    rmID = roomCode + roomNum
    filepath = "/lsfnl/alskdd"
    
    
    #uid = session['uid'] FIGURE OUT WHAT THIS WILL BE 
    postconn = db.getConn(DB)
    pid = db.insertReview(postconn, uid, rmID, rating, review, filepath)
    
    # try:
    #     #add everything but the imgpath to the Post table
    
    #     f = request.files["upload"]

    #     ext = f.filename.split('.')[-1]
    #     filename = secure_filename('{}.{}'.format(pid,ext))
    #     user_folder = os.path.join(app.config['UPLOADS'],str(uid))

    
    #     #if user folder doesn't exist, create it. Otherwise, upload it
    #     if not(os.path.isdir(user_folder)):
    #         os.mkdir(user_folder)
    #     pathname = os.path.join(user_folder,filename)
    #     f.save(pathname)
        
    #     #add the renamed imgpath into the Post table
    #     filePath = os.path.join('images/{}/'.format(uid), filename)

       
    #    # db.insertFilepath(postconn, filePath, pid)

   # flash('Upload successful')
    return redirect(url_for('roomReview', rmID = rmID))

@app.route('/search/')
def searchHome():
    return render_template("search.html")


#handler for searching
@app.route('/roomsearch/', methods=["POST"])
def search():
    roomCode = request.form.get("rCode")
    print(roomCode)
    roomNum = request.form.get("rNum")
    print(roomNum)
    query = roomCode + roomNum
    #print("query: " + query)
    #print("query length: " + str(len(query)))
    return redirect(url_for('roomResults', searched = query))

#results page for rooms search (placeholder. Once individual room pages are set up, 
#we can just direct to eh actual room page, unles someone searched by hall. )
@app.route('/roomResults/<searched>')
def roomResults(searched):
    ''' returns a list of shops that serve the searched drink.
    shows address after shop name to avoid confusion with 
    chains of the same name'''
    conn = db.getConn(DB)
    result = db.getSearchedRooms(conn, searched)
    if (len(searched) <= 4) or (not result): #return list of rooms in that hall or no results.  
        return render_template('searchResults.html',
                            rooms = result, searched = searched)
    else:
        return redirect(url_for('roomReview', rmID = searched))
 
# #individual review page for one room. 
#need to add error handling/sanitizing params. 
@app.route('/reviews/<rmID>')
def roomReview(rmID):
    conn = db.getConn(DB)
    result = db.getRoomInfo(conn, rmID)
    r = db.getAverageRating(conn, rmID)
    return render_template('indivRoom.html', rmID = rmID, reviews = result, 
        avg = r)        





if __name__ == '__main__':
    import sys, os

    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1950):
            print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
