#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import rospy
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult

class GoalSetter(QWidget):
    def __init__(self):
        super().__init__()

        # ROS Node başlat
        rospy.init_node('goal_setter_gui', anonymous=True)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        self.goal_sub = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_status_callback)
        rospy.sleep(1)  # Publisher'ın hazır olması için biraz bekle

        # Hedef koordinatları
        self.goals = {
            1: (3.72, 0.29),
            2: (3.81, -1.36),
            3: (1.38, 0.52),
            4: (1.14, -1.69),
            5: (-1.93, 0.23),
            6: (-1.75, -2.03),
            7: (-4.58, 1.31),
            8: (-4.65, -2.71)
        }

        # Arayüz butonları
        layout = QVBoxLayout()
        for i in range(1, 9):
            button = QPushButton(f"Hedef {i}")
            button.clicked.connect(self.create_button_callback(i))  # Buton callback fonksiyonuna goal indexini geçiriyoruz
            layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle("TurtleBot Kontrol Arayüzü")
        self.show()

    def create_button_callback(self, goal_index):
        """Buton callback fonksiyonu oluşturma"""
        return lambda: self.set_goal(goal_index)  # Lambda, belirli bir goal indexini geçiriyor

    def set_goal(self, goal_number):
        if goal_number in self.goals:
            x, y = self.goals[goal_number]
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
            
            rospy.loginfo(f"Hedef {goal_number} gönderiliyor: x={x}, y={y}")
            self.goal_pub.publish(goal)

    def goal_status_callback(self, msg):
        if msg.status.status == 3:  # Hedefe ulaşıldı durumu
            rospy.loginfo("Hedefe ulaşıldı.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    goal_setter = GoalSetter()
    sys.exit(app.exec())
    rospy.spin()

