#!/usr/bin/env python
'''Runs the webserver and serves the Kinect data from port 5000.'''

from __future__ import print_function, division
import ctypes

from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.wsgi import WSGIServer

import kinect

DEBUG = False

ORDER = [
    'footleft',
    'footright',
    'ankleleft',
    'ankleright',
    'kneeleft',
    'kneeright',
    'hipcenter',
    'hipleft',
    'hipright',
    'spine',
    'handleft',
    'handright',
    'wristleft',
    'wristright',
    'elbowleft',
    'elbowright',
    'shouldercenter',
    'shoulderleft',
    'shoulderright',
    'head'
]


def create_error_message_popup(message, title="Error"):
    '''Creates a popup for any error messages or alerts.'''
    ctypes.windll.user32.MessageBoxA(0, message, title, 0)


def convert_joint(json):
    '''Converts a joint into RAW format (returns the x, y, z, and w values,
    separated by space)'''
    return ' '.join(map(str, (json['x'], json['y'], json['z'], json['w'])))


def convert_skeleton(json):
    '''Converts a skeleton into RAW format (Returns joint data in the order
    defined in the ORDER constant, separated by newlines).'''
    return '\n'.join(convert_joint(json[name]) for name in ORDER)


def convert_multiple_skeletons(json):
    '''Converts multiple skeletons into RAW format (concats two
    skeleton data together)'''
    return convert_skeleton(json[1]) + '\n' + convert_skeleton(json[2])


def format_data(json, data_type):
    '''Formats data as in either JSON or RAW format.'''
    form = request.args.get('format')
    ret_json = form is None or form.lower() == 'json'
    if ret_json:
        return jsonify(json)
    else:
        if data_type == 'multiple':
            return convert_multiple_skeletons(json)
        elif data_type == 'single':
            return convert_skeleton(json)
        elif data_type == 'joint':
            return convert_joint(json)
        else:
            return str(json)


def setup():
    app = Flask(__name__, static_url_path='/static')
    CORS(app)
    kinect_data = kinect.KinectData()

    @app.route("/")
    def index():
        if request.args.get('format') == 'json':
            return jsonify(kinect_data.data)
        else:
            return convert_multiple_skeletons(kinect_data.match())

    @app.route("/demo")
    def demo():
        return app.send_static_file("demo.html")

    @app.route("/skeletons")
    def skeletons():
        return format_data(kinect_data.match(), 'multiple')
        return jsonify(kinect_data.match())

    @app.route("/skeletons/<int:skeleton_number>")
    def skeleton(skeleton_number):
        return format_data(kinect_data.match(skeleton_number), 'single')

    @app.route("/skeletons/<int:skeleton_number>/<joint>")
    def skeleton_joint(skeleton_number, joint):
        return format_data(kinect_data.match(skeleton_number, joint), 'joint')

    @app.route("/skeletons/<int:skeleton_number>/<joint>/<coord>")
    def skeleton_joint_coord(skeleton_number, joint, coord):
        return str(kinect_data.match(skeleton_number, joint, coord))

    @app.route("/num_tracked")
    def num_tracked():
        return str(kinect_data.get_num_tracked())
        
    @app.route("/tracked_players")
    def tracked_players():
        if request.args.get('format') == 'json':
            return jsonify(kinect_data.get_tracked_players())
        else:
            return ' '.join(map(str, sorted(kinect_data.get_tracked_players())))

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
