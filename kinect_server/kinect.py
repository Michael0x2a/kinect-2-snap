#!/usr/bin/env/python
"""
Provides support for interfacing with the kinect via pykinect and providing
skeletal data.
"""

from __future__ import print_function, division

from pykinect import nui
from pykinect.nui import JointId

import heapq
import time
import threading

# BYOB screen's coordinate system starts from -240 to 240 along the x axis, and
# -180 to 180 along the y axis.
WIDTH = 240 * 2
HEIGHT = 180 * 2
NUM_PLAYERS = 2

JOINTS = {
    'ankleleft': JointId.AnkleLeft,
    'ankleright': JointId.AnkleRight,
    'elbowleft': JointId.ElbowLeft,
    'elbowright': JointId.ElbowRight,
    'footleft': JointId.FootLeft,
    'footright': JointId.FootRight,
    'handleft': JointId.HandLeft,
    'handright': JointId.HandRight,
    'head': JointId.Head,
    'hipcenter': JointId.HipCenter,
    'hipleft': JointId.HipLeft,
    'hipright': JointId.HipRight,
    'kneeleft': JointId.KneeLeft,
    'kneeright': JointId.KneeRight,
    'shouldercenter': JointId.ShoulderCenter,
    'shoulderleft': JointId.ShoulderLeft,
    'shoulderright': JointId.ShoulderRight,
    'spine': JointId.Spine,
    'wristleft': JointId.WristLeft,
    'wristright': JointId.WristRight
}


def normalize(pos):
    '''Normalizes the Kinect's coordinate system to BYOB coordinates.
    Returns 'z' as the the distance of the joint in millimeters from the
    Kinect. Returns the 'w' value unchanged.'''
    output = nui.SkeletonEngine.skeleton_to_depth_image(pos, WIDTH, HEIGHT)
    return {
        'x': output[0] - WIDTH // 2,
        'y': -(output[1] - HEIGHT // 2),
        'z': pos.z * 1000,
        'w': pos.w
    }


def get_player_ids(num_players):
    return range(1, num_players + 1)


class KinectProcess(threading.Thread):
    '''Launches a separate thread which monitors the Kinect and updates
    its internal data with each frame update. To start the process, call
    the 'start' method; to end it call the 'stop' method (NOT the
    `join` method).'''
    def __init__(self, data, lock):
        '''Accepts a dictionary to store `data` and a `Threading.lock` object
        to synchronize the data.
        '''
        super(KinectProcess, self).__init__(name='KinectProcess')
        self.data = data
        self.lock = lock

        self.stop_flag = threading.Event()
        self.kinect_ready_flag = threading.Event()
        self.encountered_error_flag = threading.Event()
        self.exception = None
        
        self.prev = []
        
        self.players = {}
        self.available = get_player_ids(NUM_PLAYERS)
        self.available.reverse()

        self._init_data(NUM_PLAYERS)

    def _init_data(self, num_players):
        with self.lock:
            self.data['num_tracked'] = 0
            self.data['tracked_players'] = []
            self.data['skeletons'] = {}
            for i in get_player_ids(num_players):
                self.data['skeletons'][i] = {}
                for name in JOINTS:
                    self.data['skeletons'][i][name] = {
                        'x': 0,
                        'y': 0,
                        'z': 0,
                        'w': 0
                    }

    def _set_data(self, player_number, skeleton):
        '''Synchronizes the skeleton data'''
        with self.lock:
            for name, joint_id in JOINTS.items():
                pos = skeleton.SkeletonPositions[joint_id]
                normalized = normalize(pos)
                for coord in 'xyzw':
                    self._set_coord(player_number, name, coord, normalized[coord])
                    
    def _clear_data(self, player_number):
        with self.lock:
            for name in JOINTS:
                self.data['skeletons'][player_number][name] = {
                    'x': 0,
                    'y': 0,
                    'z': 0,
                    'w': 0
                }

    def _set_coord(self, skeleton_number, joint_name, coord, value):
        self.data['skeletons'][skeleton_number][joint_name][coord] = value

    def run(self):
        '''Sets up the Kinect data and begins watching for updates.'''
        def display(frame):
            '''Will be called every time the Kinect has a new frame.
            Processes and synchronizes that data.'''
            tracked_enum = nui.SkeletonTrackingState.TRACKED
            index = 1
            current = []
            data = {}
            for index, skeleton in enumerate(frame.SkeletonData):
                if skeleton.eTrackingState == tracked_enum:
                    data[index + 1] = skeleton
                    current.append(index)
            
            if self.prev != current:
                self.prev = current
                for index, player_number in self.players.items():
                    if index not in data:
                        # player with that id just left
                        self.available.append(player_number)
                        self.available.sort(reverse=True)
                        del self.players[index]
                        self._clear_data(player_number)
                    
                for index, skeleton in data.items():
                    player_number = self.players.get(index, None)
                    if player_number is None:
                        # set new player number, using the lowest one available
                        player_number = self.available.pop()
                        self.players[index] = player_number
                    self._set_data(player_number, skeleton)
            else:
                for index, skeleton in data.items():
                    self._set_data(self.players[index], skeleton)
                    
            self.data['num_tracked'] = index
            self.data['tracked_players'] = list(self.players.values())

        try:
            with nui.Runtime() as kinect:
                kinect.skeleton_engine.enabled = True
                kinect.skeleton_frame_ready += display

                #kinect.video_stream.open(
                #    nui.ImageStreamType.Video,
                #    2,
                #    nui.ImageResolution.Resolution640x480,
                #    nui.ImageType.Color)
                kinect.depth_stream.open(
                    nui.ImageStreamType.Depth,
                    2,
                    nui.ImageResolution.Resolution320x240,
                    nui.ImageType.Depth)

                self.kinect_ready_flag.set()
                self._block()
        except Exception as ex:
            self.kinect_ready_flag.set()
            self.encountered_error_flag.set()
            self.exception = ex
            raise

    def _block(self):
        '''Blocks the thread until the thread is manually stopped.'''
        while True:
            if self.is_stopped():
                break

    def stop(self):
        '''Calling this method will (eventually) stop this thread.'''
        self.stop_flag.set()

    def is_stopped(self):
        '''Returns `true` if the entire thread is finished.'''
        return self.stop_flag.isSet()

    def is_ready(self):
        '''Returns `true` if the Kinect has been fully initialized
        and is ready to read data.'''
        return self.kinect_ready_flag.isSet()

    def encountered_error(self):
        '''Returns 'true' if the Kinect encountered an error
        at any point.'''
        return self.encountered_error_flag.isSet()


class KinectData(object):
    '''A wrapper object providing better support for retrieving data
    from the Kinect process'''
    def __init__(self):
        '''Initializes the wrapper and the underlying thread.'''
        self.data = {}
        self.lock = threading.Lock()
        self.process = KinectProcess(self.data, self.lock)
        self.process.daemon = True

    def start(self):
        '''Starts the underlying Kinect thread.'''
        self.process.start()
        while not self.process.is_ready():
            time.sleep(0.5)
        if self.process.encountered_error():
            raise self.process.exception

    def end(self):
        '''Ends the underlying Kinect thread.'''
        self.process.stop()

    def match(self, skeleton_number=None, joint=None, coord=None):
        '''Returns all joint data that corresponds to the provided
        skeleton, joint, and coord. Will perform a case-insensitive match.

        Example:

            >>> kinect_data.match(1, 'HandLeft', 'x')
            {
                '1handleftx': 32
            }

            >>> kinect_data.match(1, 'HandLeft')
            {
                '1handleftx': 32,
                '1handlefty': -100.3,
                '1handleftz': 821,
                '1handleftw': 1.0
            }
        '''
        joint = self._format_key(joint)
        coord = self._format_key(coord)
        
        if skeleton_number == 0:
            if self.data['num_tracked'] > 0:
                skeleton_number = min(self.data['tracked_players'])
            else:
                skeleton_number = 1

        if skeleton_number is None:
            return self.data['skeletons']
        elif joint is None:
            return self.data['skeletons'][skeleton_number]
        elif coord is None:
            return self.data['skeletons'][skeleton_number][joint]
        else:
            return self.data['skeletons'][skeleton_number][joint][coord]

    def get_num_tracked(self):
        '''Returns the number of skeletons currently being tracked.'''
        return self.data['num_tracked']
        
    def get_tracked_players(self):
        '''Returns the ids of the players that are currently tracked.
        Valid returns values are:
        
        []
        [1]
        [2]
        [1, 2]
        '''
        return self.data['tracked_players']

    def _format_key(self, value):
        if value is None:
            return None
        else:
            return value.lower().replace('_', '').replace('-', '')


def main():
    '''Launches just the Kinect thread, and prints out the head coordinate
    data of the first player for debugging purposes.'''
    try:
        print("Starting Kinect process")
        kinect_data = KinectData()
        kinect_data.start()

        print("Ready")
        while True:
            time.sleep(1)
            print(kinect_data.match(1, 'Head'))
    except KeyboardInterrupt:
        kinect_data.end()
    except:
        kinect_data.end()
        raise

if __name__ == '__main__':
    main()
