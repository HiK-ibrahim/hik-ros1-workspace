#!/usr/bin/env python

import rospy
from sensor_msgs.msg import CameraInfo

def camera_info_callback(data):
    rospy.loginfo(f"Camera Info: {data}")

def main():
    rospy.init_node('camera_info_listener', anonymous=True)
    rospy.Subscriber('/front_cam/camera/camera_info', CameraInfo, camera_info_callback)
    rospy.spin()

if __name__ == '__main__':
    main()

