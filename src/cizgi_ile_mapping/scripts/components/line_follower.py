import rospy
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from qr_detection import detect_qr_codes
from line_detection import follow_line, search_for_line
from obstacle_avoidance import ObstacleAvoidance  # Engel algılama sınıfını ekledik
import cv2
import subprocess
import time

class LineFollower:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw', Image, self.image_callback)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.twist = Twist()
        self.line_following = False
        self.map_scanned = False
        self.qr_last_detected_time = rospy.Time.now().to_sec()
        self.start_time = rospy.Time.now().to_sec()
        self.searching = False
        self.slam_started = False
        self.map_found = False
        self.goal_started = False  # Hedefe gitme işlemi başlatıldı mı kontrolü

        # Engel algılama sınıfını başlatıyoruz
        self.obstacle_avoidance = ObstacleAvoidance(cmd_vel_topic="/cmd_vel", scan_topic="/scan")

        # Haritanın varlığını kontrol et ve navigasyonu başlat
        map_path = "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal.yaml"
        if os.path.exists(map_path):
            rospy.loginfo("Kayıtlı harita bulundu. Navigasyon başlatılıyor.")
            self.start_navigation(map_path)
            self.map_found = True  # Harita mevcut işaretlendi
        else:
            rospy.loginfo("Kayıtlı harita bulunamadı. QR kodu tarayarak SLAM başlatılacak.")

        self.prev_time = time.time()  # İlk zaman kaydını başlatıyoruz
        self.frame_count = 0  # FPS hesaplamak için kare sayacı
        self.fps = None  # FPS başlangıç değeri None olarak ayarlandı

    def start_navigation(self, map_path):
        try:
            subprocess.Popen(["xterm", "-e", "roslaunch", "turtlebot3_navigation", "turtlebot3_navigation.launch", f"map_file:={map_path}"])
            self.map_scanned = True
            rospy.loginfo("Navigasyon başlatıldı.")
        except Exception as e:
            rospy.logerr(f"Navigasyon başlatılamadı: {e}")

    def image_callback(self, msg):
        # FPS hesaplama
        current_time = time.time()
        self.frame_count += 1
        time_diff = current_time - self.prev_time

        if time_diff >= 1:  # 1 saniye geçtiyse FPS'i hesapla
            self.fps = self.frame_count / time_diff
            self.prev_time = current_time
            self.frame_count = 0

        # Engel algılama kontrolü
        if self.obstacle_avoidance.is_avoiding_obstacle():
            return  # Engel kaçınma modu aktifse diğer algoritmalar devre dışı bırakılır.

        self.obstacle_avoidance.run()  # Engel algılama algoritması çalıştırılır

        # Eğer harita mevcutsa QR kodu algılama ve çizgi izleme işlemlerini atla
        if self.map_found:
            # Harita bulunduğunda hedefe gitme işlemi sadece bir kez başlatılmalı
            if not self.goal_started:
                try:
                    rospy.loginfo("Harita bulundu, Hedefe gitme işlemi başlatılıyor.")
                    subprocess.Popen(["xterm", "-hold", "-e", "bash", "-c", "sleep 5; python3 /home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/cizgi_ile_mapping/scripts/components/hedeflere_git.py"])
                    self.goal_started = True  # Hedefe gitme işlemi başlatıldı
                except Exception as e:
                    rospy.logerr(f"Hedefe gitme işlemi başlatılamadı: {e}")
            return

        # Harita yoksa QR kodu algılama ve çizgi izlemeyi başlat
        image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        detect_qr_codes(self, image)

        if self.line_following:
            follow_line(self, image)
        else:
            search_for_line(self)

        # FPS'i görüntü üzerine yazma (eğer FPS hesaplanmışsa)
        if self.fps is not None:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, f"FPS: {self.fps:.2f}", (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Kamera", image)
        cv2.waitKey(1)

