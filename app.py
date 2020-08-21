from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)


from werkzeug.utils import secure_filename
app = Flask(__name__)

import os
import dbi
import imghdr
import db 
import dbi # database stuff
import json

DB = 'dormir'

@app.route('/')
def index():
    if "username" in session:
       return redirect(url_for("home"))
    return render_template('home.html', page_title='Dormir')


@app.route('/profile/')
def profile():
    # if "username" in session:
    #    return redirect(url_for("profile"))
    conn = db.getConn(DB)
    #uid = get it from session. 
    uid = 1 #temporary.
    rooms = db.getMyRooms(conn, uid)
    path = db.getPicPath(conn, uid)
    print(path)
    #path = "img/incognito.png"
    return render_template('profile.html', page_title='Dormir', my_rooms = rooms, pic = path)   

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
    if (len(searched) <= 4) or (not result): #return list of rooms in that hall. 
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

#ajax handler for bookmarking/starring a room. 
@app.route('/star/', methods=["POST"])
def star():
    conn = db.getConn(DB)
    rmID = request.form.get('rmID')
    uid = 1
    #actual version:
    #uid = session['uid']
    alreadyStarred = db.alreadyStarred(conn, uid, rmID)
    if not alreadyStarred:
        db.updateStarred(conn, uid, rmID)

    return jsonify({'starred': alreadyStarred})

#handler for delete review (my room)
@app.route('/deleteReview/', methods = ["POST"])
def deleteReview():
    conn = db.getConn(DB)
    room = request.form.get('rmID')
    uid = getUid(conn, session['CAS_USERNAME'])
    db.deleteReview(conn, uid, room)
    print(room, " review deleted")
    return redirect(request.referrer)

@app.route('/changePfp', methods = ["POST"])
def pic():
    conn = db.getConn(DB)
    uid = db.getUid(conn, username)
    #uid = 1
    #upload folder path, and allowed extension of file images
    #check if this exists
    # username = "zwang11"
    username = session['CAS_USERNAME']
    path = 'static/img/{}'.format(username)
    # print(path)
    # print(os.path.exists(path))
    if not os.path.exists(path):
        os.mkdir('static/img/{}'.format(username))
    UPLOAD_FOLDER = 'static/img/{}/'.format(username)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

    #add code to change file name
    #check allowed files 
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files['newpic']
    filePath = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) #get the filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #save the file to the upload folder destination
        filePath = os.path.join('img/{}/'.format(username), filename) #make a modified path so the profile.html can read it
        db.changePfp(conn, uid, filePath)
        print('successfully updated.')
    return redirect(request.referrer)


if __name__ == '__main__':
    # import sys,os
    # if len(sys.argv) > 1:
    #     # arg, if any, is the desired port number
    #     port = int(sys.argv[1])
    #     assert(port>1024)
    # else:
    #     port = os.getuid()
    # app.debug = True
    #app.run('0.0.0.0',port)
    app.run()