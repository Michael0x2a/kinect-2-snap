#!/usr/bin/env/python
"""
Provides support for interfacing with the kinect via pykinect and providing
skeletal data.
"""

from __future__ import print_function, division

from pykinect import nui
from pykinect.nui import JointId

import time
import multiprocessing

# BYOB screen's coordinate system starts from -240 to 240 along the x axis, and
# -180 to 180 along the y axis.
WIDTH = 240 * 2
HEIGHT = 180 * 2

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
    'kneereft': JointId.KneeLeft,
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


class KinectProcess(multiprocessing.Process):
    '''Launches a separate process which monitors the Kinect and updates
    its internal data with each frame update. To start the process, call
    the 'start' method; to end it call the 'join' method.'''
    def __init__(self, data):
        '''"data" must be a 'multiprocessing.Manager.dict' object, and
        is used to synchronize data across different processes.
        '''
        super(KinectProcess, self).__init__(name='KinectProcess')
        self.data = data
        self.data['num_tracked'] = 0

    def _set_data(self, skeleton_number, skeleton):
        '''Synchronizes the skeleton data'''
        for name, joint_id in JOINTS.items():
            key = str(skeleton_number) + name
            pos = skeleton.SkeletonPositions[joint_id]
            normalized = normalize(pos)
            for coord in 'xyzw':
                # Note: since `self.data` is not a normal dict, it isn't
                # save to include nested data structures since they won't
                # be correctly synchronized across processes.
                #
                # Use `self.data` as a key-value store only.
                self.data[key + coord] = normalized[coord]

    def run(self):
        '''Sets up the kinect data and begins watching for updates.'''
        def display(frame):
            '''Will be called every time the Kinect has a new frame.
            Processes and synchronizes that data.'''
            index = 0
            tracked_enum = nui.SkeletonTrackingState.TRACKED
            for skeleton in frame.SkeletonData:
                if skeleton.eTrackingState == tracked_enum:
                    index += 1
                    self._set_data(index, skeleton)
            self.data['num_tracked'] = index

        with nui.Runtime() as kinect:
            kinect.skeleton_engine.enabled = True
            kinect.skeleton_frame_ready += display

            kinect.video_stream.open(
                nui.ImageStreamType.Video,
                2,
                nui.ImageResolution.Resolution640x480,
                nui.ImageType.Color)
            kinect.depth_stream.open(
                nui.ImageStreamType.Depth,
                2,
                nui.ImageResolution.Resolution320x240,
                nui.ImageType.Depth)

            while True:
                pass


class KinectData(object):
    '''A wrapper object providing better support for retrieving data
    from the Kinect process'''
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.data = self.manager.dict()
        self.process = KinectProcess(self.data)

    def start(self):
        '''Starts the underlying Kinect process.'''
        self.process.start()

    def end(self):
        '''Ends the underlying Kinect process.'''
        self.process.join()

    def match(self, skeleton_number='', joint='', coord=''):
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
        match = '{0}{1}{2}'.format(skeleton_number, joint, coord)
        match = match.lower().replace('_', '')
        match_func = lambda k: match in k and k != 'num_tracked'

        return {k: v for k, v in self.data.items() if match_func(k)}

    def get(self, key):
        '''Retrieves the data associated with the provided key
        (case-insensitive). If no data is associated with the key,
        returns None.

        Example:

            >>> kinect_data.get('1handleftx')
            32

        '''
        key = key.lower().replace('_', '')
        if key in self.data:
            return self.data[key]
        else:
            return None

    def get_num_tracked(self):
        '''Returns the number of skeletons currently being tracked.'''
        return self.data['num_tracked']


def main():
    '''Launches just the Kinect process, and prints out the head coordinate
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
    # Required to prevent exe creators such as Pyinstaller, cx_freeze, and p2exe
    # from derping out on Windows.
    #
    # Don't move the below call from its current position -- the docs were
    # relatively insistent that `multiprocessing.freeze_support()` needs to go
    # directly below `if __name__ == '__main__'`, and I don't know what magic
    # they're doing nor if it's safe to refactor it into `main`.
    multiprocessing.freeze_support()
    main()
