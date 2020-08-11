from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)



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
    rooms = db.getMyRooms(conn, 1)
    return render_template('profile.html', page_title='Dormir', my_rooms = rooms)   



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