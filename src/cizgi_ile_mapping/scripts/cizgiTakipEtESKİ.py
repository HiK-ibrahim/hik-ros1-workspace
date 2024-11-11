#!/usr/bin/env python

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
import pyzbar.pyzbar as pyzbar
import time

class LineFollower:
    def __init__(self):
        # ROS ile OpenCV arasında köprü oluşturma
        self.bridge = CvBridge()
        
        # Kameradan gelen görüntüleri dinlemek için subscriber
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw', Image, self.image_callback)
        
        # Robotu yönlendirmek için publisher
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        
        # Twist mesajı
        self.twist = Twist()
        
        # Çizgi takip durumunu belirleyen bayrak
        self.line_following = False
        self.qr_last_detected_time = 0  # QR kodu en son tespit edildiği zaman
        self.qr_detection_timeout = 5  # QR kodu okunduktan sonra bekleme süresi

    def image_callback(self, msg):
        # ROS Image mesajını OpenCV formatına çevir
        image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # QR kodlarını tespit et
        self.detect_qr_codes(image)

        if self.line_following:
            # Görüntüde kırmızı çizgiyi tespit et (yalnızca alt üçte bir)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, lower_red, upper_red)

            # Görüntünün alt kısmındaki (yakın alan) kırmızı çizgiyi bul
            h, w = mask.shape
            search_top = 1 * h // 4  # Görüntünün alt çeyreğini dikkate al
            mask[0:search_top, 0:w] = 0  # Üst kısımdaki pikselleri sıfırla
            
            # Kırmızı çizgiyi görüntüde bul
            M = cv2.moments(mask)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])  # Çizginin merkezi
                cy = int(M['m01'] / M['m00'])

                # Çizginin merkezini görüntüde işaretle
                cv2.circle(image, (cx, cy), 10, (0, 0, 255), -1)

                # Çizgiye göre robotu yönlendirme
                err = cx - w / 2
                self.twist.linear.x = 0.2
                self.twist.angular.z = -float(err) / 500
                self.cmd_vel_pub.publish(self.twist)
            else:
                # Çizgi bulunamadığında önce yavaş bir tarama yap, sonra genişlet
                rospy.loginfo("Çizgi bulunamadı, yavaşça tarıyor...")
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.1  # Küçük açılar için yavaşça dön
                self.cmd_vel_pub.publish(self.twist)
        else:
            # Çizgi takip edilmiyor, robot duracak
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0
            self.cmd_vel_pub.publish(self.twist)

        # Sonucu ekranda göster
        cv2.imshow("Kamera", image)
        cv2.waitKey(1)

    def detect_qr_codes(self, image):
        # QR kodlarını tanımlama
        decoded_objects = pyzbar.decode(image)
        current_time = time.time()  # Mevcut zaman

        # QR kodu tespit edildiğinde
        if decoded_objects and (current_time - self.qr_last_detected_time) > self.qr_detection_timeout:
            for obj in decoded_objects:
                if obj.data == b'HiK-RacLab':  # QR kodun içeriğini kontrol et
                    rospy.loginfo(f"QR Kodu Okundu: {obj.data.decode('utf-8')}")
                    self.line_following = True
                    self.qr_last_detected_time = current_time  # QR kodu tespit zamanı güncelle
                    rospy.loginfo("Çizgi takip başlatıldı.")
                    break  # QR kodu okuduktan sonra döngüyü kır


if __name__ == '__main__':
    rospy.init_node('line_follower')
    line_follower = LineFollower()
    rospy.spin()

