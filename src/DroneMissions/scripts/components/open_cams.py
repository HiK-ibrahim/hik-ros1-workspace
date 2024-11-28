#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2

class CameraHandler:
    def __init__(self, topic, window_name):
        self.topic = topic
        self.window_name = window_name
        self.bridge = CvBridge()
        self.image = None
        self.updated = False  # Görüntü yenilendi mi?

        rospy.Subscriber(self.topic, Image, self.callback)

    def callback(self, data):
        try:
            self.image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.updated = True  # Yeni görüntü geldi
        except CvBridgeError as e:
            rospy.logerr(f"CV Bridge Error ({self.window_name}): {e}")

    def show_image(self):
        if self.image is not None and self.updated:
            cv2.imshow(self.window_name, self.image)
            self.updated = False  # Görüntü işlendi

