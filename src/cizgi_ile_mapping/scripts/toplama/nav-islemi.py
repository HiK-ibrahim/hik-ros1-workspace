#!/usr/bin/env python3
import rospy
import subprocess
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
import actionlib

class GoalSetter:
    def __init__(self):
        rospy.init_node('goal_setter', anonymous=True)
        
        # Publisher ve Subscriber kurulumları
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        self.goal_sub = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_status_callback)
        
        # Hedef koordinatları
        self.goals = [
            (-1.33, 1.62),  # 1. hedef
            (1.05, 1.61)    # 2. hedef
        ]
        self.current_goal_index = 0
        self.map_loaded = False  # Harita yüklenme durumunu takip et
        self.start_navigation()

    def start_navigation(self):
        # Map server'ı başlatmak için subprocess kullanıyoruz
        rospy.loginfo("Harita başlatılıyor...")
        map_file = "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap/cizgiVeQRMapSONHal.yaml"
        subprocess.Popen(["rosrun", "map_server", "map_server", map_file])
        rospy.sleep(5)  # Harita yüklendikten sonra biraz bekle
        
        # Move base'i başlatıyoruz
        rospy.loginfo("Move base başlatılıyor...")
        subprocess.Popen(["roslaunch", "move_base", "move_base.launch"])
        rospy.sleep(5)  # Move base yüklendikten sonra biraz bekle

        self.map_loaded = True  # Harita yüklendi
        rospy.loginfo("Harita yüklendi, hedefler gönderilmeye başlanacak.")
        self.set_next_goal()

    def set_next_goal(self):
        if self.map_loaded and self.current_goal_index < len(self.goals):
            x, y = self.goals[self.current_goal_index]
            goal = PoseStamped()
            goal.header.frame_id = "map"  # Frame ID "map" olarak ayarlandı
            goal.header.stamp = rospy.Time.now()  # Zaman damgasını güncelle
            goal.pose.position.x = x
            goal.pose.position.y = y
            goal.pose.position.z = 0.0
            goal.pose.orientation.x = 0.0
            goal.pose.orientation.y = 0.0
            goal.pose.orientation.z = 0.0
            goal.pose.orientation.w = 1.0

            rospy.loginfo(f"Hedef gönderiliyor: x={x}, y={y}")
            self.goal_pub.publish(goal)
        else:
            rospy.loginfo("Harita yüklenmedi veya tüm hedefler tamamlandı.")

    def goal_status_callback(self, msg):
        if msg.status.status == 3:  # Hedefe ulaşıldı durumu
            rospy.loginfo(f"Hedefe ulaşıldı: {self.goals[self.current_goal_index]}")
            self.current_goal_index += 1
            self.set_next_goal()  # Sonraki hedefe geç

if __name__ == '__main__':
    goal_setter = GoalSetter()
    rospy.spin()

