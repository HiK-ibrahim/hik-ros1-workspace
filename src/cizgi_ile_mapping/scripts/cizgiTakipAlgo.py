#!/usr/bin/env python

import rospy
import cv2
import numpy as np
import subprocess
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
import pyzbar.pyzbar as pyzbar
import time
import math
import yaml

class LineFollower:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw', Image, self.image_callback)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.twist = Twist()
        
        # Çizgi takip ve QR kod durumları
        self.line_following = False
        self.qr_last_detected_time = 0
        self.qr_detection_timeout = 5
        self.initial_search_timeout = 2
        self.start_time = time.time()
        self.map_scanned = False
        
        # Çizgi kaybı sonrası arama yönleri
        self.searching = False
        self.search_start_time = None
        self.search_direction = 1  # İlk yön: saat yönünde
        self.search_angle_duration = 75  # 75 derece dönüş
        self.current_angle = 0  # Başlangıçtaki açı
        self.direction_switched = False  # Yön değişimi kontrolü

        # Harita kontrolü
        self.map_path = '/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal.yaml'  # YAML harita dosyanızın yolu
        self.map_loaded = False

        # Hedef konumlar
        self.target_positions = [
            (2.0, 2.0),  # Örnek 1. hedef
            (5.0, 5.0),  # Örnek 2. hedef
        ]

    def check_map(self):
        """Harita dosyasını kontrol et"""
        if os.path.exists(self.map_path):
            rospy.loginfo("Harita dosyası mevcut.")
            self.map_loaded = True
        else:
            rospy.loginfo("Harita dosyası mevcut değil, QR kod taraması yapılacak.")
            self.map_loaded = False

    def go_to_position(self, position):
        """Belirtilen konuma gitmek için komut yayınla"""
        target_x, target_y = position
        # Burada hedefe gitmek için ROS komutları eklenebilir
        rospy.loginfo(f"Hedefe gidiliyor: {target_x}, {target_y}")
        # Örneğin, robotu bir hedefe yönlendirebilirsiniz.

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        self.detect_qr_codes(image)

        if self.map_loaded:
            # Harita yüklendiyse, hedeflere git
            for position in self.target_positions:
                self.go_to_position(position)
                # Hedefe ulaşıldığında, hedefi güncellemek için arada bir bekleme eklenebilir.
            return

        if self.line_following:
            # Çizgi takip kodları
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, lower_red, upper_red)

            h, w = mask.shape
            search_top = 3 * h // 5
            mask[0:search_top, 0:w] = 0
            
            M = cv2.moments(mask)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.circle(image, (cx, cy), 10, (0, 0, 255), -1)

                err = cx - w / 2
                self.twist.linear.x = 0.2
                self.twist.angular.z = -float(err) / 500
                self.cmd_vel_pub.publish(self.twist)
                
                # Çizgi bulundu, arama modunu sıfırla
                self.searching = False
            else:
                # Çizgiyi kaybettiğinde arama moduna geç
                if not self.searching:
                    self.searching = True
                    self.search_start_time = time.time()
                    self.current_angle = 0  # Başlangıçta açı sıfırlanır
                    self.search_direction = 1  # İlk yön: saat yönünde dön
                    self.direction_switched = False  # Yön değiştirilmedi
                else:
                    # Yön değiştirme işlemi
                    if not self.direction_switched:
                        # İlk 75 dereceyi saat yönünde dönecek
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = 0.3 * self.search_direction
                        self.cmd_vel_pub.publish(self.twist)

                        # Açı arttır
                        self.current_angle += abs(self.twist.angular.z)  # Her adımda dönen açı
                        if self.current_angle >= self.search_angle_duration:
                            self.direction_switched = True  # Yön değişti
                            self.current_angle = 0  # Açı sıfırlanır
                    else:
                        # Yön değiştirdi, şimdi ters yönde 150 derece dönecek
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = -0.3 * self.search_direction  # Ters yön
                        self.cmd_vel_pub.publish(self.twist)

                        # Açı arttır
                        self.current_angle += abs(self.twist.angular.z)
                        if self.current_angle >= 150:  # 150 derece döndü
                            self.search_direction *= -1  # Yönü değiştir (saat yönü/tersi)
                            self.direction_switched = False  # Yön değiştirme sırası sıfırlanır
                            self.current_angle = 0  # Açı sıfırlanır

        else:
            # İlk başta QR araması için 2 saniye içinde bulamazsa dönerek ara
            if time.time() - self.start_time < self.initial_search_timeout:
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.3
                self.cmd_vel_pub.publish(self.twist)
            else:
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.0
                self.cmd_vel_pub.publish(self.twist)

        cv2.imshow("Kamera", image)
        cv2.waitKey(1)

    def detect_qr_codes(self, image):
        decoded_objects = pyzbar.decode(image)
        current_time = time.time()

        if decoded_objects and (current_time - self.qr_last_detected_time) > self.qr_detection_timeout:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                
                if qr_data == 'HiK-RacLab':
                    rospy.loginfo(f"QR Kodu Okundu: {qr_data}")
                    self.line_following = True
                    self.qr_last_detected_time = current_time
                    rospy.loginfo("Çizgi takip başlatıldı.")

                    break
                elif qr_data == 'MapTarandiQR' and not self.map_scanned:
                    rospy.loginfo("MAP tarama tamamlandı.")
                    # Alttaki 2 satır mapı kayıt ediyor.
                    map_save_command = "rosrun map_server map_saver -f /home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal"
                    process = subprocess.Popen(['xterm',  '-e', map_save_command])
                    
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
                    self.cmd_vel_pub.publish(self.twist)
                    self.line_following = False
                    self.map_scanned = True
                    break

if __name__ == '__main__':
    rospy.init_node('line_follower')
    line_follower = LineFollower()
    line_follower.check_map()  # Harita var mı kontrol et
    rospy.spin()

