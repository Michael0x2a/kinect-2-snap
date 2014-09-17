#!/usr/bin/env python
'''Runs the webserver and serves the Kinect data from port 5000.'''

from __future__ import print_function, division
import ctypes

from flask import Flask, jsonify
from flask_cors import CORS
from gevent.wsgi import WSGIServer

import kinect

DEBUG = False


def create_error_message_popup(message, title="Error"):
    ctypes.windll.user32.MessageBoxA(0, message, title, 0)


def json_to_key_value(json):
    return jsonify(json)


def setup():
    app = Flask(__name__, static_url_path='/static')
    CORS(app)
    kinect_data = kinect.KinectData()

    @app.route("/")
    def index():
        return jsonify(kinect_data.data)

    @app.route("/demo")
    def demo():
        return app.send_static_file("demo.html")

    @app.route("/skeletons")
    def skeletons():
        return jsonify(kinect_data.match())

    @app.route("/skeletons/<int:skeleton_number>")
    def skeleton(skeleton_number):
        return jsonify(kinect_data.match(skeleton_number))

    @app.route("/skeletons/<int:skeleton_number>/<joint>")
    def skeleton_joint(skeleton_number, joint):
        return jsonify(kinect_data.match(skeleton_number, joint))

    @app.route("/skeletons/<int:skeleton_number>/<joint>/<coord>")
    def skeleton_joint_coord(skeleton_number, joint, coord):
        return str(kinect_data.match(skeleton_number, joint, coord))

    @app.route("/num_tracked")
    def num_tracked():
        return str(kinect_data.get_num_tracked())

    @app.route("/heartbeat")
    def heartbeat():
        return "ok"

    return app, kinect_data


def run_production_webserver(app):
    http_webserver = WSGIServer(('', 5000), app, log=None)
    http_webserver.serve_forever()


def run_debug_webserver(app):
    app.run(debug=True, use_reloader=False)


def run_webserver(app):
    if DEBUG:
        run_debug_webserver(app)
    else:
        run_production_webserver(app)


def main():
    print("Setting up data...")
    app, kinect_data = setup()
    try:
        print("Connecting to the Kinect...")
        kinect_data.start()

        print("Ready! Hit `Ctrl+c` to end.\n")
        run_webserver(app)
    except KeyboardInterrupt:
        print("Closing Kinect connection...")
        kinect_data.end()

        print("Goodbye!")
    except WindowsError:
        create_error_message_popup(
            "Could not connect to the Kinect!\n"
            "\n"
            "Please consult the README for more information.")
        raise
    except:
        create_error_message_popup("Encountered an unknown error!")
        raise

if __name__ == '__main__':
    main()
