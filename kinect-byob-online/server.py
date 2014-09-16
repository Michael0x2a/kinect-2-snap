#!/usr/bin/env python
'''Runs the webserver and serves the Kinect data from port 5000.'''

from __future__ import print_function, division

import multiprocessing

from flask import Flask
from flask_cors import CORS

import kinect

def json_to_key_value(json):
    return '\n'.join('{}={}'.format(*pair) for pair in json.items())


def setup():
    app = Flask(__name__)
    CORS(app)
    kinect_data = kinect.KinectData()

    @app.route("/")
    def index():
        return json_to_key_value(kinect_data.data)


    @app.route("/skeletons")
    def skeletons():
        return json_to_key_value(kinect_data.match())


    @app.route("/skeletons/<int:skeleton_number>")
    def skeleton(skeleton_number):
        return json_to_key_value(kinect_data.match(skeleton_number))


    @app.route("/skeletons/<int:skeleton_number>/<joint>")
    def skeleton_joint(skeleton_number, joint):
        return json_to_key_value(kinect_data.match(skeleton_number, joint))


    @app.route("/skeletons/<int:skeleton_number>/<joint>/<coord>")
    def skeleton_joint_coord(skeleton_number, joint, coord):
        return json_to_key_value(kinect_data.match(skeleton_number, joint, coord))


    @app.route("/num_tracked")
    def num_tracked():
        return str(kinect_data.get_num_tracked())


    @app.route("/joint/<target>")
    def joint(target):
        data = kinect_data.get(target)
        return str(data) if data is not None else ''


    @app.route("/heartbeat")
    def heartbeat():
        return "ok"

    return app, kinect_data

def main():
    app, kinect_data = setup()
    try:
        kinect_data.start()
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        kinect_data.end()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
