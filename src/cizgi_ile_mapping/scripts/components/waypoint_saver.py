#!/usr/bin/env python

import rospy
import os  # Dosya yolunu ayarlamak için gerekli
from nav_msgs.msg import Odometry

class WaypointSaver:
    def __init__(self):
        rospy.init_node('waypoint_saver', anonymous=True)
        self.previous_position = None  # Önceki waypoint
        self.min_distance_threshold = 0.5  # Minimum mesafe eşiği (metre)

        # Betiğin bulunduğu dizini belirleyip dosya yolunu ayarla
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, "waypoints.txt")

        # Dosyayı temizleyerek başlat
        with open(self.file_path, "w") as file:
            file.write("x, y\n")

        # Odometry verisini dinleyen subscriber
        self.odom_subscriber = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        rospy.loginfo(f"Waypoint saver çalışıyor... Kaydedilecek dosya: {self.file_path}")

    def odom_callback(self, msg):
        # Mevcut pozisyonu al
        current_position = msg.pose.pose.position

        # İlk waypoint kaydediliyor
        if self.previous_position is None:
            self.save_waypoint(current_position)
            self.previous_position = current_position
            return

        # Önceki pozisyon ile mevcut pozisyon arasındaki mesafeyi hesapla
        distance = self.calculate_distance(self.previous_position, current_position)
        if distance >= self.min_distance_threshold:
            self.save_waypoint(current_position)
            self.previous_position = current_position

    def calculate_distance(self, previous, current):
        """İki pozisyon arasındaki Öklid mesafesini hesapla"""
        return ((current.x - previous.x) ** 2 + (current.y - previous.y) ** 2) ** 0.5

    def save_waypoint(self, position):
        """Waypoint'i dosyaya kaydeder ve terminale yazdırır"""
        with open(self.file_path, "a") as file:
            file.write(f"{position.x}, {position.y}\n")
        rospy.loginfo(f"Waypoint kaydedildi: x={position.x}, y={position.y}")

if __name__ == "__main__":
    try:
        saver = WaypointSaver()
        rospy.spin()  # ROS düğümünü aktif tut
    except rospy.ROSInterruptException:
        pass

