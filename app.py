from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)
from flask_cas import CAS



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

@app.route('/')
def index():
    #if "username" in session:
     #  return redirect(url_for("home"))
    return render_template('review.html', page_title='review')

@app.route('/upload/', methods=["POST"])
def upload(): 
    '''adds a post's information into the database'''
    roomCode = request.form.get("rCode")
    roomNum = request.form.get("rNum")
    rating = request.form.get("rating")
    review = request.form.get("review")

    uid = 10
    rmID = roomCode + roomNum
    username = session['CAS_USERNAME']
    #uid = session['uid'] FIGURE OUT WHAT THIS WILL BE 
    postconn = db.getConn(DB)

    #upload folder path, and allowed extension of file images
    UPLOAD_FOLDER = 'static/img/{}/'.format(uid)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

    #check allowed files 
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files['profpic']
    filePath = None
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) #get the filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #save the file to the upload folder destination
            filePath = os.path.join('img/{}/'.format(uid), filename) #make a modified path so the profile.html can read it
            pid = db.insertReview(postconn, rmID, rating, review, filepath)
            return redirect(url_for('review', username = username, review = review, filepath = filepath, rmID))
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