from flask import Flask
import servertime

app = Flask(__name__)

numRequests = 0

@app.route('/')
def hello_world():
    return '<h1>Hello Everyone!</h1>'

@app.route('/about')
def about():
    global numRequests
    numRequests += 1
    return ('''<h1>Hello, World!</h1>
<p>This is Scott's version</p>
<p>The time on Tempest is {time}.</p>
<p>There have been {n} requests so far.</p>'''
    .format(time=servertime.now(),n=numRequests))

@app.route('/bye')
def bye():
    return 'This is how we say good-bye!!'

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)