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

if __name__ == "__main__":
    rospy.init_node("multi_camera_view", anonymous=True)

    # Kameralar için handler oluştur
    front_camera = CameraHandler('/front_cam/camera/image', "Front Camera")
    downward_camera = CameraHandler('/downward_cam/downward_camera/image', "Downward Camera")

    rate = rospy.Rate(30)  # OpenCV penceresini 30 FPS ile güncelle

    while not rospy.is_shutdown():
        # Görüntüleri göster
        front_camera.show_image()
        downward_camera.show_image()

        # OpenCV penceresi güncellenmesi için gerekli
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        rate.sleep()

    # OpenCV pencerelerini kapat
    cv2.destroyAllWindows()

