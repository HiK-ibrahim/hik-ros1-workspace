#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
import actionlib

class GoalSetter:
    def __init__(self):
        rospy.init_node('goal_setter', anonymous=True)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        self.goal_sub = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_status_callback)
        rospy.sleep(1)  # Publisher'ın hazır olması için biraz bekle

        # Hedef koordinatları
        self.goals = [
            (-1.33, 1.62),
            (1.05, 1.61),
            (3.02, -1.10),
            (2.34, -2.93),
            (-1.47, -3.05)
        ]
        self.current_goal_index = 0
        self.set_next_goal()

    def set_next_goal(self):
        if self.current_goal_index < len(self.goals):
            x, y = self.goals[self.current_goal_index]
            goal = PoseStamped()
            goal.header.frame_id = "map"  # Frame ID "map" olarak ayarla
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
            rospy.loginfo("Tüm hedefler tamamlandı.")

    def goal_status_callback(self, msg):
        if msg.status.status == 3:  # Hedefe ulaşıldı durumu
            rospy.loginfo(f"Hedefe ulaşıldı: {self.goals[self.current_goal_index]}")
            self.current_goal_index += 1
            self.set_next_goal()  # Sonraki hedefe geç

if __name__ == '__main__':
    goal_setter = GoalSetter()
    rospy.spin()

