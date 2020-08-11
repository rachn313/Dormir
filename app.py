from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)



app = Flask(__name__)

import os
import dbi
import imghdr
import bcrypt
#import db # database stuff
import json
import db

DB = 'rnavarr2_db' #CHANGE

@app.route('/')
def index():
    #if "username" in session:
     #  return redirect(url_for("home"))
    return render_template('home.html', page_title='Dormir')

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

    uid = 10
    rmID = roomCode + roomNum
    filepath = "/lsfnl/alskdd"
    
    
    #uid = session['uid'] FIGURE OUT WHAT THIS WILL BE 
    postconn = db.getConn(DB)
    pid = db.insertReview(postconn, rmID, rating, review, filepath)
    
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

if __name__ == '__main__':
    import sys,os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)