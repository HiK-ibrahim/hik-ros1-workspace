#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
import time

class GoalSetter:
    def __init__(self):
        rospy.init_node('goal_setter', anonymous=True)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        self.goal_sub = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_status_callback)
        rospy.sleep(1)

        # Hedef koordinatları
        self.goals = [
        
            (1.14, -1.69),
            (2.85, -5.27),
            

       
        ]
        self.current_goal_index = 0  # İlk hedefin indeksini başlat

    def set_next_goal(self):
        # Sıradaki hedefi ayarla ve gönder
        if self.current_goal_index < len(self.goals):
            x, y = self.goals[self.current_goal_index]
            goal = PoseStamped()
            goal.header.frame_id = "map"
            goal.header.stamp = rospy.Time.now()
            goal.pose.position.x = x
            goal.pose.position.y = y
            goal.pose.position.z = 0.0
            goal.pose.orientation.x = 0.0
            goal.pose.orientation.y = 0.0
            goal.pose.orientation.z = 0.0
            goal.pose.orientation.w = 1.0
            
            # Hedefi gönder
            rospy.loginfo(f"Hedefe gönderiliyor: X = {x}, Y = {y}")
            self.goal_pub.publish(goal)

    def goal_status_callback(self, msg):
        if msg.status.status == 3:  # Hedefe ulaşıldı durumu
            rospy.loginfo(f"Hedefe ulaşıldı: {self.goals[self.current_goal_index]}")
            # Bir sonraki hedefe geç
            self.current_goal_index += 1
            if self.current_goal_index < len(self.goals):
                rospy.sleep(1)  # Hedefler arasında kısa bir bekleme süresi
                self.set_next_goal()

if __name__ == '__main__':
    goal_setter = GoalSetter()
    goal_setter.set_next_goal()
    rospy.spin()

