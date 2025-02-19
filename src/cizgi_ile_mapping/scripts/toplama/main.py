#!/usr/bin/env python

import rospy
from line_follower import LineFollower

if __name__ == '__main__':
    rospy.init_node('line_follower')
    line_follower = LineFollower()
    rospy.spin()

