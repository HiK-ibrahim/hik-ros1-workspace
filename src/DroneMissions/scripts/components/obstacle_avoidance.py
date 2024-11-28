#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoidance:
    def __init__(self):
        # ROS abonelik ve yayıncı tanımları
        self.lidar_sub = rospy.Subscriber('/scan', LaserScan, self.lidar_callback)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Engel algılama parametreleri
        self.min_distance_threshold = 0.6  # Engel algılama mesafesi (metre)
        self.closest_distance = float('inf')  # İlk durumda sonsuz
        self.avoidance_mode = False  # Kaçınma modu aktif mi?

        # ROS döngü hızı
        self.rate = rospy.Rate(10)  # 10 Hz

    def lidar_callback(self, scan_data):
        """
        LIDAR verilerini işleyerek belirli bir açı aralığındaki mesafeleri değerlendirir.
        """
        front_angles = range(len(scan_data.ranges) // 3, 2 * len(scan_data.ranges) // 3)  # Ön bölge (60°-120°)
        distances = [scan_data.ranges[i] for i in front_angles if 0.1 < scan_data.ranges[i] < 10.0]
        if distances:
            self.closest_distance = min(distances)
        else:
            self.closest_distance = float('inf')

    def stop_drone(self):
        """
        Drone'u durdurur.
        """
        stop_cmd = Twist()
        self.cmd_vel_pub.publish(stop_cmd)
        rospy.loginfo("Drone durduruldu.")

    def move_in_curve(self, direction, duration, forward_speed=0.1, turn_speed=0.9):
        """
        Drone'u kavisli bir şekilde hareket ettirir.
        """
        rospy.loginfo(f"Kavisli hareket: {'Sağa' if direction == 'right' else 'Sola'}")

        cmd = Twist()
        cmd.linear.x = forward_speed
        cmd.angular.z = turn_speed if direction == "right" else -turn_speed

        start_time = rospy.Time.now()
        while (rospy.Time.now() - start_time).to_sec() < duration and not rospy.is_shutdown():
            self.cmd_vel_pub.publish(cmd)
            self.rate.sleep()

        self.stop_drone()  # Hareket sonrası drone'u durdur

    def avoid_obstacle(self):
        """
        Engel kaçınma işlemini uygular.
        """
        rospy.loginfo("Engel algılandı, kaçınma işlemi başlatılıyor.")
        self.avoidance_mode = True

        while self.closest_distance < self.min_distance_threshold and not rospy.is_shutdown():
            rospy.loginfo(f"Mevcut mesafe: {self.closest_distance} m, Eşik: {self.min_distance_threshold} m")

            # 1. Adım: Geriye ve sola kavisli dönüş
            self.move_in_curve("left", duration=2)

            # 2. Adım: Mesafeyi tekrar kontrol et
            rospy.sleep(1)  # Bir süre bekle
            if self.closest_distance >= self.min_distance_threshold:
                rospy.loginfo("Engel temizlendi.")
                break

        self.avoidance_mode = False

    def run(self):
        """
        Drone'un sürekli engel algılama ve kaçınma döngüsünü çalıştırır.
        """
        rospy.loginfo("Engel algılama başlatıldı.")
        while not rospy.is_shutdown():
            if self.closest_distance < self.min_distance_threshold and not self.avoidance_mode:
                self.avoid_obstacle()
            else:
                # Engel yoksa düz ilerle
                cmd = Twist()
                cmd.linear.x = 0.5  # İleri hareket
                self.cmd_vel_pub.publish(cmd)
            self.rate.sleep()

if __name__ == '__main__':
    rospy.init_node('obstacle_avoidance')
    obstacle_avoidance = ObstacleAvoidance()
    try:
        obstacle_avoidance.run()
    except rospy.ROSInterruptException:
        pass
