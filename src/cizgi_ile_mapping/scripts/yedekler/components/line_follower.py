import rospy
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from qr_detection import detect_qr_codes
from line_detection import follow_line, search_for_line
import cv2
import subprocess

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

        # Haritanın varlığını kontrol et ve navigasyonu başlat
        map_path = "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal.yaml"
        if os.path.exists(map_path):
            rospy.loginfo("Kayıtlı harita bulundu. Navigasyon başlatılıyor.")
            self.start_navigation(map_path)
            self.map_found = True  # Harita mevcut işaretlendi
        else:
            rospy.loginfo("Kayıtlı harita bulunamadı. QR kodu tarayarak SLAM başlatılacak.")

    def start_navigation(self, map_path):
        try:
            subprocess.Popen(["xterm", "-e", "roslaunch", "turtlebot3_navigation", "turtlebot3_navigation.launch", f"map_file:={map_path}"])
            self.map_scanned = True
            rospy.loginfo("Navigasyon başlatıldı.")
        except Exception as e:
            rospy.logerr(f"Navigasyon başlatılamadı: {e}")

    def image_callback(self, msg):
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

        cv2.imshow("Kamera", image)
        cv2.waitKey(1)

