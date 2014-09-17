#!/usr/bin/env python
'''Runs the webserver and serves the Kinect data from port 5000.'''

from __future__ import print_function, division

from flask import Flask
from flask_cors import CORS

from gevent.wsgi import WSGIServer 

import ctypes

import kinect


def create_error_message_popup(message, title="Error"):
    ctypes.windll.user32.MessageBoxA(0, message, title, 0)

def json_to_key_value(json):
    return '\n'.join('{}={}'.format(*pair) for pair in json.items())

counter = 0 

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
        #global counter 
        #counter = (counter + 10) % 100
        #return str(counter)
    
        data = kinect_data.get(target)
        return str(data) if data is not None else ''


    @app.route("/heartbeat")
    def heartbeat():
        return "ok"

    return app, kinect_data

def main():
    print("Setting up data...")
    app, kinect_data = setup()
    try:
        print("Connecting to the Kinect...")
        kinect_data.start()
        
        print("Starting webserver...")
        http_webserver = WSGIServer(('', 5000), app, log=None)
        
        print("Ready! Hit `Ctrl+c` to end.\n")
        http_webserver.serve_forever()
    except KeyboardInterrupt:
        print("Closing Kinect connection...")
        kinect_data.end()
        
        print("Goodbye!")
    except WindowsError:
        create_error_message_popup(
            "Could not connect to the Kinect!\n"
            "\n"
            "Please consult the README for more information.")
    except:
        create_error_message_popup("Encountered an unknown error!")

if __name__ == '__main__':
    main()
