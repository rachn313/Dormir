from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)



app = Flask(__name__)

import os
import dbi
import imghdr
#import bcrypt
#import db # database stuff
import json


@app.route('/')
def index():
    if "username" in session:
       return redirect(url_for("home"))
    return render_template('home.html', page_title='Dormir')


@app.route('/profile/')
def profile():
    # if "username" in session:
    #    return redirect(url_for("profile"))
    return render_template('profile.html', page_title='Dormir')   



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