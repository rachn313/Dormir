from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)
from flask_cas import CAS
from werkzeug import secure_filename


app = Flask(__name__)
app.secret_key = 'rosebud'  # so we can have sessions, which are necessary

import os
import dbi
import imghdr
import bcrypt
#import db # database stuff
import json
import db

DB = 'rnavarr2_db' #CHANGE

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
    return render_template('base.html') 

application = app


@app.route('/')
def index():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        profpicPath = 'img/default_profilepic.jpg'
        username = session['CAS_USERNAME']
        attribs = session['CAS_ATTRIBUTES']
        firstName = attribs['cas:givenName']
        lastName = attribs['cas:sn']
        fullname = firstName + ' ' + lastName
        conn = db.getConn(DB)
        curs = dbi.cursor(conn)
        curs.execute('''SELECT * FROM Users WHERE username = %s''', [username])
        row = curs.fetchone()
        if row is None:
            curs.execute('''INSERT INTO Users(fullname, username, profpicPath) VALUES(%s,%s,%s)''', [fullname, username, profpicPath])
        curs.execute('select last_insert_id()')
        row = curs.fetchone()
        uid = row[0]
        session['username'] = username
        session['uid'] = uid
        return render_template('home.html')
    #print('Session keys: ',list(session.keys()))
    #for k in list(session.keys()):
     #   print(k,' => ',session[k])
    else:
        return render_template('base.html')

@app.route('/upload/', methods=["POST"])
def upload(): 
    '''adds a post's information into the database'''
    roomCode = request.form.get("rCode")
    roomNum = request.form.get("rNum")
    rating = request.form.get("rating")
    review = request.form.get("review")

    uid = session['uid']
    rmID = roomCode + roomNum
    roomID = roomCode + ' ' + roomNum
    username = session['CAS_USERNAME']
    #uid = session['uid'] FIGURE OUT WHAT THIS WILL BE 
    postconn = db.getConn(DB)
    if roomCode == 'MCA':
        building = 'McAfee'
  
    #upload folder path, and allowed extension of file images
    UPLOAD_FOLDER = 'static/img/{}/'.format(username)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

    #check allowed files 
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files['upload']
    filePath = None
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) #get the filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #save the file to the upload folder destination
            #filePath = os.path.join('img/{}/'.format(uid), filename) #make a modified path so the profile.html can read it
            db.insertReview(postconn, uid, rmID, rating, review, filepath)
            return redirect(url_for('review', username = username, rating = rating, review = review, filepath = filepath, roomID = roomID))
    
    return redirect(url_for('index'))

    #except Exception as err:
    #     print("upload failed because " + str(err))
    #     flash('Upload failed {why}'.format(why=err))
    #     return redirect( url_for('index') )


#@app.route('/profile/')
#def profile():
    # if "username" in session:
    #    return redirect(url_for("profile"))
 #   return render_template('profile.html', page_title='Profile')   

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

@app.route('/reviews/<rmID>')
def roomReview(rmID):
    conn = db.getConn(DB)
    result = db.getRoomInfo(conn, rmID)
    r = db.getAverageRating(conn, rmID)
    username = session['CAS_USERNAME']
    return render_template('review.html', rmID = rmID, reviews = result, 
        avg = r, username = username)    


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