#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np


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


class LineFollower:
    def __init__(self, camera_handler, vel_pub):
        self.camera_handler = camera_handler
        self.cmd_pub = vel_pub  # Hız komutları için yayıncı
        self.target_x = 320  # Görüntü genişliğinin ortası (varsayılan değer)
        self.kp = 0.01  # Orantısal kontrol kazancı

    def process_image(self):
        if self.camera_handler.image is None or not self.camera_handler.updated:
            return

        # Görüntü işleme
        cv_image = self.camera_handler.image

        # BGR görüntüyü HSV renk uzayına dönüştür
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Kırmızı rengin HSV aralığını tanımla
        lower_red = np.array([0, 50, 50])  # Düşük kırmızı tonları
        upper_red = np.array([10, 255, 255])  # Yüksek kırmızı tonları
        lower_red2 = np.array([170, 50, 50])  # Kırmızı rengin diğer tonları
        upper_red2 = np.array([180, 255, 255])  # Yüksek kırmızı tonları

        # Maskeler oluştur
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        # İki maskeyi birleştir
        mask = cv2.bitwise_or(mask1, mask2)

        # Maske üzerinden konturları bul
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # En büyük konturu al
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)

            if M["m00"] > 0:
                # Çizginin orta noktasını hesapla
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Görüntü üzerinde orta noktayı göster
                cv2.circle(cv_image, (cx, cy), 5, (0, 255, 0), -1)

                # Çizgiyle hizalanmak için hata hesapla
                error = self.target_x - cx

                # Dronu kontrol etmek için hız komutlarını gönder
                cmd = Twist()
                cmd.linear.x = 0.5  # İleri hız (sabit)
                cmd.angular.z = -self.kp * error  # Dönme hızı (hata ile orantılı)
                self.cmd_pub.publish(cmd)

        # İşlenmiş görüntüyü ve maskeyi göster
        cv2.imshow(self.camera_handler.window_name, cv_image)
        cv2.imshow(f"{self.camera_handler.window_name} Mask", mask)
        self.camera_handler.updated = False  # Görüntü işlendi


def move_up(vel_pub):
    # Yükselmek için komut gönder
    rospy.loginfo("Moving Up")
    vel_msg = Twist()
    vel_msg.linear.z = 1.0  # Yükselme komutu
    vel_pub.publish(vel_msg)
    rospy.sleep(1)  # Bir süre beklemek için


if __name__ == "__main__":
    rospy.init_node("multi_camera_line_follower", anonymous=True)

    # Kameralar için handler oluştur
    front_camera = CameraHandler('/front_cam/camera/image', "Front Camera")
    downward_camera = CameraHandler('/downward_cam/downward_camera/image', "Downward Camera")

    # Hız komutları için publisher oluştur
    vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    # Başlangıçta yükselme komutu gönder
    move_up(vel_pub)

    # LineFollower nesnesi oluştur
    line_follower = LineFollower(downward_camera, vel_pub)

    rate = rospy.Rate(30)  # OpenCV penceresini 30 FPS ile güncelle

    while not rospy.is_shutdown():
        # Ön kamerayı göster
        front_camera.show_image()

        # Çizgi takibi işle
        line_follower.process_image()

        # OpenCV penceresi güncellenmesi için gerekli
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        rate.sleep()

    # OpenCV pencerelerini kapat
    cv2.destroyAllWindows()

