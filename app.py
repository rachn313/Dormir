from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, Response, jsonify)
from flask_cas import CAS
from werkzeug import secure_filename


app = Flask(__name__)
app.secret_key = 'rosebud'  # so we can have sessions, which are necessary

import os
import dbi
import imghdr
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

@app.before_first_request
def startup():
    #db.init_db()
    # clear out any prior session
    session.clear()

@app.route('/logged_in/')
def logged_in():
    flash('successfully logged in!')
    return redirect( url_for('index') )

@app.route('/after_logout/')
def after_logout():
    flash('successfully logged out!')
    return redirect(url_for('index'))

application = app

@app.route('/')
def index():
    try: 
        conn = db.getConn(DB)
        if 'CAS_USERNAME' in session:
            username = session['CAS_USERNAME']
            profpicPath = 'img/default_profilepic.jpg'
            username = session['CAS_USERNAME']
            attribs = session['CAS_ATTRIBUTES']
            firstName = attribs['cas:givenName']
            lastName = attribs['cas:sn']
            fullname = firstName + ' ' + lastName
            curs = dbi.cursor(conn)
            curs.execute('''SELECT * FROM Users WHERE username = %s''', [username])
            row = curs.fetchone()
            if row is None:
                curs.execute('''INSERT INTO Users(fullname, username, profpicPath) VALUES(%s,%s,%s)''', [fullname, username, profpicPath])
                conn.commit()
              
            uid = db.getUid(conn,username)
            conn.close()
            return render_template('home.html')
        else:
            if db.existsReview(conn) == True:
                randomrmID = db.randomReviewoftheDay(conn)
                randomRoom = db.getRoomInfo(conn, randomrmID.get('rmID'))
                allRooms = db.getallRooms(conn)
                topRooms = {}
                for roomID in allRooms:
                    rating = db.getAverageRating(conn,roomID.get('rmID'))
                    topRooms[roomID.get('rmID')] = rating.get('rate')
                sort_rooms = sorted(topRooms.items(), key=lambda x: x[1], reverse=True)
                if len(allRooms) >= 3:
                    three = True
                    two = False
                    one = False 
                    top1 = sort_rooms[0][0]
                    top1Rating = sort_rooms[0][1]
                    img1 = db.getImgfromRmID(conn, top1)
                    top2 = sort_rooms[1][0]
                    top2Rating = sort_rooms[1][1]
                    img2 = db.getImgfromRmID(conn, top2)
                    top3 = sort_rooms[2][0]
                    top3Rating = sort_rooms[2][1]
                    img3 = db.getImgfromRmID(conn, top3)
                    conn.close()
                    return render_template('base.html', randomRoom= randomRoom[0], top1 = top1, top1Rating = top1Rating, img1 = img1, top2 = top2, top2Rating = top2Rating, img2 = img2, top3 = top3, top3Rating = top3Rating, img3 = img3, three = three, two = two, one = one)   
                elif len(allRooms) == 2:
                    two = True
                    three = False
                    one = False
                    top1 = sort_rooms[0][0]
                    top1Rating = sort_rooms[0][1]
                    img1 = db.getImgfromRmID(conn, top1)
                    top2 = sort_rooms[1][0]
                    top2Rating = sort_rooms[1][1] 
                    img2 = db.getImgfromRmID(conn, top2)
                    print(img2)
                    conn.close()
                    return render_template('base.html', randomRoom = randomRoom[0], top1 = top1, top1Rating = top1Rating, img1 = img1, top2 = top2, top2Rating = top2Rating, img2 = img2, two = two, one = one, three = three)   
                elif len(allRooms) == 1:
                    one = True
                    two = False
                    three = False
                    top1 = sort_rooms[0][0]
                    top1Rating = sort_rooms[0][1]
                    img1 = db.getImgfromRmID(conn, top1)
                    conn.close()
                    return render_template('base.html', randomRoom = randomRoom[0], top1 = top1, top1Rating = top1Rating, img1 = img1, one=one, two = two, three = three)
            else:
                one = False
                two = False
                three = False
                return render_template('base.html', one = one, two = two, three= three)
    except Exception as err:
        flash('login error ' + str(err))
        return redirect(request.referrer)

@app.route('/team/', methods=["GET"])
def team():
    return render_template('team.html')

@app.route('/upload/', methods=["POST", "GET"])
def upload(): 
    '''adds a post's information into the database'''
    roomCode = request.form.get("rCode")
    flash(roomCode)
    roomNum = request.form.get("rNum")
    rating = request.form.get("rating")
    review = request.form.get("review")
    rmID = roomCode + roomNum
    username = session['CAS_USERNAME']
    flash(username)
    try: 
        postconn = db.getConn(DB)
        uid = db.getUid(postconn, username)
        if db.checkReview(postconn, uid, rmID):
            flash('Already posted a review. Go to your profile to edit your review!')
            return redirect(url_for('index'))
        #upload folder path, and allowed extension of file images
        #check if this exists
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'static/img/{}'.format(username))
        if not os.path.exists(path):
            os.mkdir(path)
        UPLOAD_FOLDER = path
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

        #add code to change file name
        #check allowed files 
        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        uid = db.getUid(postconn, username)
        file = request.files['upload']
        flash(file)
        #flash(file)
        #flash(file.filename)
       # print("FILE:")
        #print(file)
        if file.filename == '': #check if they uploaded an img
            filePath = 'NA'
            db.insertReview(postconn, uid, rmID, rating, review, filePath)
            return redirect(url_for('roomReview', rmID = rmID))

        filePath = None
        flash(allowed_file(file.filename))
        if file and allowed_file(file.filename):
                flash('made it to here')
                filename = secure_filename(file.filename) #get the filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #save the file to the upload folder destination
                filePath = os.path.join('img/{}/'.format(username), filename) #make a modified path so the profile.html can read it
                db.insertReview(postconn, uid, rmID, rating, review, filePath)
                return redirect(url_for(request.referrer))
        
        return redirect(url_for('index'))

    except Exception as err:
    #     print("upload failed because " + str(err))
        flash('Upload failed {why}'.format(why=err))
        return redirect(request.referrer)


@app.route('/profile/')
def profile():
    if session['CAS_USERNAME']:
        try:
            conn = db.getConn(DB)
            username = session['CAS_USERNAME']
            uid = db.getUid(conn, username)
            rooms = db.getMyRooms(conn, uid)
            path = db.getPicPath(conn, uid)
            savedRooms = db.getSaved(conn, uid)
            conn.close()
            return render_template('profile.html', page_title='Dormir', my_rooms = rooms, pic = path, username = username, starred_rooms = savedRooms) 
        except Exception as err:
            flash('profile failed to load due to {why}'.format(why=err))
            return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@app.route('/changePfp/', methods = ["POST", "GET"])
def pic():
    conn = db.getConn(DB)
    username = session['CAS_USERNAME']
    uid = db.getUid(conn, username)
    
    
    path = 'static/img/{}'.format(username)
    # print(path)
    # print(os.path.exists(path))
    try: 
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'static/img/{}'.format(username))
        if not os.path.exists(path):
            os.mkdir(path)
        UPLOAD_FOLDER =  path
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
            conn.close()
        conn.close()
        return redirect(request.referrer)
    except Exception as err:
        flash(repr(err))
        return redirect(request.referrer)

#handler for searching
@app.route('/roomsearch/', methods=["POST"])
def search():
    roomCode = request.form.get("rCode")
    #print(roomCode)
    roomNum = request.form.get("rNum")
    #print(roomNum)
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
    if 'CAS_USERNAME' in session:
        conn = db.getConn(DB)
        result = db.getSearchedRooms(conn, searched)
        conn.close()
        if (len(searched) <= 4) or (not result): #return list of rooms in that hall or no results.  
            return render_template('searchResults.html',
                                rooms = result, searched = searched)
        else:
            return redirect(url_for('roomReview', rmID = searched))
    else: #not logged in:
        return redirect(url_for('index'))

@app.route('/reviews/<rmID>', methods= ["GET"])
def roomReview(rmID):
    try: 
        if 'CAS_USERNAME' in session:
            conn = db.getConn(DB)
            result = db.getRoomInfo(conn, rmID) 
            building = ''
            #print("RMID first three letters")
            #print(rmID[0:3])
            if rmID[0:3] == 'MCA':
                building = 'McAfee'
            elif rmID[0:3] == 'BEB':
                building = 'Beebe'
            elif rmID[0:3] == 'BAT':
                building = 'Bates'
            elif rmID[0:3] == 'CAS':
                building = 'Casa Cervantes'
            elif rmID[0:3] == 'CAZ':
                building = 'Cazenove'
            elif rmID[0:3] == 'CLA':
                building = 'Claflin'
            elif rmID[0:3] == 'DAV':
                building = 'Stone-DAVIS'
            elif rmID[0:3] == 'DOW':
                building = 'Dower'
            elif rmID[0:3] == 'FRE':
                building = 'Freeman'
            elif rmID[0:3] == 'FRH':
                building = 'French House'
            elif rmID[0:3] == 'HEM':
                building = 'Hemlock Apartments'
            elif rmID[0:3] == 'INS':
                building = 'Instead'
            elif rmID[0:3] == 'LAK':
                building = 'Lakehouse'
            elif rmID[0:3] == 'MUN':
                building = 'Munger'
            elif rmID[0:3] == 'ORC':
                building = 'Orchid Apartments'
            elif rmID[0:3] == 'POM':
                building = 'Pomeroy'
            elif rmID[0:3] == 'SEV':
                building = 'Severance'
            elif rmID[0:3] == 'SHA':
                building = 'Shafer'
            elif rmID[0:3] == 'STO':
                building = 'STONE-davis'
            elif rmID[0:3] == 'TCE':
                building = 'Tower Court'
            elif rmID[0:3] == 'TCW':
                building = 'Tower Court'
            
            if (building == 'Tower Court' or building == 'Lakehouse' or building == 'Severance' or building == 'Claflin'):
                diningHall = 'Lulu/Tower'
            elif (building == 'Beebe' or building == 'Munger' or building == 'Shafer' or building == 'Pomeroy' or building == 'Cazenove'):
                diningHall = 'Pomeroy/Lulu'
            else:
                diningHall = 'Bates/Stone-Davis'

            username = session['CAS_USERNAME']
            uid = db.getUid(conn, username)
            saved = db.save_trueFalse(conn, rmID, uid)
            r = db.getAverageRating(conn, rmID)
            conn.close()
            return render_template('review.html', rmID = rmID, reviews = result, avg = r, username = username, building = building, diningHall = diningHall, saved = saved)    
        else:
            conn.close()
            return redirect(url_for('index'))
    except Exception as err:
        flash(repr(err))
        return (redirect(request.referrer))

@app.route('/saved/<rmID>', methods= ["POST"])   
def Save(rmID):
    ''' ajax function that updates saving the room'''
    try: 
        username = session['CAS_USERNAME']
        conn = db.getConn(DB)
        uid = db.getUid(conn, username)
        db.addSave(conn, rmID, uid)
        conn.close()
        return jsonify()
    except Exception as err:
        #print(err)
        return jsonify( {'error': True, 'err': str(err) } )

@app.route('/unsaved/<rmID>', methods= ["POST"])   
def Unsave(rmID):
    ''' ajax function for unsaving a room'''
    try: 
        username = session['CAS_USERNAME']
        conn = db.getConn(DB)
        uid = db.getUid(conn, username)
        db.removeSave(conn, rmID, uid)
        conn.close()
        return jsonify()
    except Exception as err:
        #print(err)
        return jsonify( {'error': True, 'err': str(err) } )


@app.route('/editReview/<rmID>', methods=["POST", "GET"])
def edit(rmID): 
    try:
        conn = db.getConn(DB)
        username = session['CAS_USERNAME']
        rating = request.form.get("rating")
        review = request.form.get("review")
        uid = db.getUid(conn, username)
        db.editReview(db.getConn(DB), uid, rating, review)
        conn.close()
        return redirect(url_for('roomReview', rmID = rmID))
    except Exception as err:
        #print(err)
        return (redirect(request.referrer))
  

    

#handler for delete review (my room)
@app.route('/deleteReview/', methods = ["POST"])
def deleteReview():
    try: 
        conn = db.getConn(DB)
        room = request.form.get('rmID')
        username = session['CAS_USERNAME']
        uid = db.getUid(conn, session['CAS_USERNAME'])
        img = db.getImgfromRmID(conn, room)
        #print(imgPath)
        db.deleteReview(conn, uid, room)
        filePath = 'static/{}'.format(img.get('imgPath'))
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, filePath)
        os.remove(path)
        #print(room, " review deleted")
        return redirect(request.referrer)
    except Exception as err:
        #print(err)
        return (redirect(request.referrer))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1950):
            #print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)