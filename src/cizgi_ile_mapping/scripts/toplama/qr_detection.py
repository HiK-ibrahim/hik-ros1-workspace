import rospy
import pyzbar.pyzbar as pyzbar
import time
import subprocess

def detect_qr_codes(line_follower, image):
    decoded_objects = pyzbar.decode(image)
    current_time = time.time()

    for obj in decoded_objects:
        qr_data = obj.data.decode('utf-8')

        # "HiK-RacLab" QR kodu algılandığında SLAM başlat, sadece bir kere çalıştır
        if qr_data == 'HiK-RacLab' and (current_time - line_follower.qr_last_detected_time) > 5:
            rospy.loginfo("QR Kodu Okundu: HiK-RacLab")

            if not line_follower.slam_started:
                line_follower.line_following = True
                line_follower.qr_last_detected_time = current_time
                rospy.loginfo("Çizgi takibi başlatılıyor.")
                
                # SLAM'i yeni bir xterm penceresinde başlat
                slam_command = ["xterm", "-e", "roslaunch turtlebot3_slam turtlebot3_slam.launch"]
                subprocess.Popen(slam_command)
                line_follower.slam_started = True  # SLAM'in açıldığını işaretle
                rospy.loginfo("SLAM başlatıldı.")

        elif qr_data == 'MapTarandiQR' and not line_follower.map_scanned:
            rospy.loginfo("MAP tarama tamamlandı.")
            map_save_command = "rosrun map_server map_saver -f /home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal"
            subprocess.Popen(['xterm', '-e', map_save_command])
            line_follower.line_following = False
            line_follower.map_scanned = True

            # Robotu durdurmak için hız komutlarını sıfırla
            line_follower.twist.linear.x = 0.0
            line_follower.twist.angular.z = 0.0
            line_follower.cmd_vel_pub.publish(line_follower.twist)
            rospy.loginfo("Robot durduruldu.")

