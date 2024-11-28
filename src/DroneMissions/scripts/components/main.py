#!/usr/bin/env python

import rospy
from takeoff import TakeoffControl  # Kalkış kontrol sınıfı
from line_follower import LineFollower  # Çizgi takip sınıfı
from open_cams import CameraHandler  # Kamera modülü
from obstacle_avoidance import ObstacleAvoidance  # Engelden kaçma sınıfı
from sensor_msgs.msg import LaserScan
import cv2
import numpy as np

class DroneControl:
    def __init__(self):
        # Kalkış ve çizgi takip sınıfları
        self.takeoff_control = TakeoffControl()
        self.line_follower = LineFollower()
        self.obstacle_avoidance = ObstacleAvoidance()

        # Kamera kontrolü için iki farklı handler
        self.front_camera = CameraHandler('/front_cam/camera/image', "Front Camera")
        self.downward_camera = CameraHandler('/downward_cam/downward_camera/image', "Downward Camera")

        # Lidar verisini alacak bir değişken
        self.lidar_data = None

        # Lidar verisi için subscriber
        rospy.Subscriber("/scan", LaserScan, self.lidar_callback)

    def lidar_callback(self, data):
        """
        Lidar verisini callback fonksiyonunda alır.
        """
        self.lidar_data = data

    def process_lidar(self, front_frame):
        """
        Lidar verisini alır ve front kamera görüntüsüne renklendirilmiş olarak ekler.
        """
        if self.lidar_data is None:
            return front_frame

        ranges = self.lidar_data.ranges
        angle_min = self.lidar_data.angle_min
        angle_increment = self.lidar_data.angle_increment

        # Front kamera görüntüsüne lidar verisini eklemek için bir resim oluşturuyoruz
        height, width = front_frame.shape[:2]
        center = (width // 2, height // 2)

        lidar_frame = np.zeros_like(front_frame)

        # Lidar verisini renkli noktalar olarak çizeriz
        for i, r in enumerate(ranges):
            if r > self.lidar_data.range_min and r < self.lidar_data.range_max:
                angle = angle_min + i * angle_increment
                x = int(center[0] + r * np.cos(angle))
                y = int(center[1] + r * np.sin(angle))

                # Lidar verisini renkli noktalar olarak işaretler
                if 0 <= x < width and 0 <= y < height:
                    # Renkli nokta
                    cv2.circle(lidar_frame, (x, y), 1, (0, 0, 255), -1)

        # Lidar görüntüsünü front kamera görüntüsüne ekleyin
        combined_frame = cv2.addWeighted(front_frame, 0.7, lidar_frame, 0.3, 0)
        return combined_frame

    def start_mission(self):
        """
        Görevi başlatır: Önce kalkış yapar, ardından çizgi takip ve engelden kaçma işlemleri başlar.
        """
        rospy.loginfo("Görev başlatılıyor: Kalkış yapılıyor...")
        self.takeoff_control.takeoff()  # Kalkış işlemini başlatır

        rospy.loginfo("Kalkış tamamlandı, görev başlıyor...")
        rate = rospy.Rate(10)  # 10 Hz döngü

        while not rospy.is_shutdown():
            # Engelden kaçma kontrolü
            self.obstacle_avoidance.avoid_obstacle()

            # Kameralardan görüntü al
            front_frame = self.front_camera.image
            downward_frame = self.downward_camera.image

            processed_frame = None
            if downward_frame is not None:
                # Aşağıya bakan kameradan gelen görüntüyü işleme
                processed_frame, direction = self.line_follower.follow_line(downward_frame)
                rospy.loginfo(f"Yön: {direction}")

            # Front kamera görüntüsüne lidar verisini ekle
            if front_frame is not None:
                combined_frame = self.process_lidar(front_frame)

                # İşlenmiş görüntüyü ekle
                if processed_frame is not None:
                    combined_frame = np.hstack((combined_frame, processed_frame))
            else:
                combined_frame = processed_frame

            # Birleştirilmiş görüntüyü göster
            cv2.imshow("HiK HECTOR Drone Camera", combined_frame)

            # OpenCV pencere kontrolü
            if cv2.waitKey(1) & 0xFF == ord('q'):
                rospy.loginfo("Görev durduruldu.")
                break

            rate.sleep()

        # Görev tamamlandığında tüm OpenCV pencerelerini kapat
        cv2.destroyAllWindows()

if __name__ == "__main__":
    rospy.init_node('drone_control', anonymous=True)

    drone_control = DroneControl()
    try:
        drone_control.start_mission()
    except rospy.ROSInterruptException:
        rospy.loginfo("Görev sonlandırıldı.")
