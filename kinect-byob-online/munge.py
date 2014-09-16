"""provides a simple PyGame sample with video, depth stream, and skeletal tracking"""

import pykinect
from pykinect import nui
from pykinect.nui import JointId

import time 
import multiprocessing

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
        
class KinectProcess(multiprocessing.Process):
    def __init__(self, data):
        super(KinectProcess, self).__init__(name='KinectProcess')
        self.data = data
        self.data['num_tracked'] = 0
            
    def _is_valid(self, skeleton):
        head_pos = skeleton.SkeletonPositions[JointId.Head]
        return head_pos.x != 0 or head_pos.y != 0
        
    def _set_data(self, index, skeleton):
        for name, joint_id in JOINTS.items():
            key = str(index) + name
            pos = skeleton.SkeletonPositions[joint_id]
            
            self.data[key + 'x'] = pos.x
            self.data[key + 'y'] = pos.y
            self.data[key + 'z'] = pos.z
            self.data[key + 'w'] = pos.w
            
    def run(self):
        def display(frame):
            index = 0
            for skeleton in frame.SkeletonData:
                if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
                    print '!!'
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
    def __init__(self):
        pass 
        
    def start(self):
        self.manager = multiprocessing.Manager()
        self.data = self.manager.dict()
        self.process = KinectProcess(self.data)
        self.process.start()
        
    def end(self):
        self.process.join()
        
    def match(self, skeleton_number='', joint='', coord=''):
        match = '{0}{1}{2}'.format(skeleton_number, joint, coord)
        match = match.lower().replace('_', '')
            
        output = []
        for key, value in self.data.items():
            if key.startswith(match) and key != 'num_tracked':
                output.append('{0}={1}'.format(key, value))
        return '\n'.join(output)
        
    def get(self, key):
        key = key.lower().replace('_', '')
        if key in self.data:
            return self.data[key]
        else:
            return ''
    
    def get_num_tracked(self):
        return self.data['num_tracked']
        
def main2():
    kinect_data = KinectData()
    kinect_data.start()
    try:
        while True:
            #print kinect_data.data['Head']
            time.sleep(1)
    except:
        kinect_data.end()
        raise
  
def main():
    skeletons = None
    
    def post_frame(frame):
        print "??"
        inspect_skeletons(frame.SkeletonData)
        
    def inspect_skeletons(skeletons):
        print "!!"
        for index, data in enumerate(skeletons):
            # draw the Head
            HeadPos = data.SkeletonPositions[JointId.Head]
            print HeadPos

            
  
    kinect = nui.Runtime()
    
    kinect.skeleton_engine.enabled = True
    kinect.skeleton_frame_ready += post_frame
    
    kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
    kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

    print "ready"
    
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main2()