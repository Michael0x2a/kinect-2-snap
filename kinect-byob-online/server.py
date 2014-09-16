#!/usr/bin/env python

from __future__ import print_function, division

from flask import Flask
from flask.ext.cors import CORS

import munge

app = Flask(__name__)
cors = CORS(app)

kinect_data = munge.KinectData()

@app.route("/")
def index():
    return str(kinect_data.data)

@app.route("/skeletons")
def skeletons():
    return kinect_data.match()
    
@app.route("/skeletons/<int:skeleton_number>")
def skeleton(skeleton_number):
    return kinect_data.match(skeleton_number)
    
@app.route("/skeletons/<int:skeleton_number>/<joint>")
def skeleton_joint(skeleton_number, joint):
    return kinect_data.match(skeleton_number, joint)
    
@app.route("/skeletons/<int:skeleton_number>/<joint>/<coord>")
def skeleton_joint_coord(skeleton_number, joint, coord):
    return kinect_data.match(skeleton_number, joint, coord)
    
@app.route("/num_tracked")
def num_tracked():
    return str(kinect_data.get_num_tracked())
    
@app.route("/joint/<target>")
def joint(target):
    return str(kinect_data.get(target))
    
def main():
    print('start')
    kinect_data.start()
    print('end start')
    app.run(debug=True, use_reloader=False)
    
    print('??')
    kinect_data.end()
        
if __name__ == '__main__':
    main()