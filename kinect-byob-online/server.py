#!/usr/bin/env python

from __future__ import print_function, division

from flask import Flask
from flask.ext.cors import CORS


app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def index():
    return 'Hello world!'
    
if __name__ == '__main__':
    app.run(debug=True)