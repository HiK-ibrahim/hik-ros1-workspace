#!/usr/bin/env python3
import sys
import rospy
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

class GoalSetter:
    def __init__(self):
        rospy.init_node('goal_setter', anonymous=True)
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
        self.goal_sub = rospy.Subscriber('/move_base/result', MoveBaseActionResult, self.goal_status_callback)
        rospy.sleep(1)

        # Hedef koordinatları
        self.goals = [
            (3.72, 0.29),
            (3.81, -1.36),
            (1.38, 0.52),
            (1.14, -1.69),
            (-1.93, 0.23),
            (-1.75, -2.03),
            (-4.58, 1.31),
            (-4.65, -2.71)
        ]
        self.current_goal_index = None  # Hedef indexini başta boş bırak

        # Arayüz oluştur
        self.init_ui()

    def init_ui(self):
        self.window = QWidget()
        self.window.setWindowTitle("Robot Hedef Belirleyici")
        layout = QVBoxLayout()

        self.label = QLabel("Hedefler: ")
        layout.addWidget(self.label)

        self.status_label = QLabel("")  # Durum etiketini oluştur
        layout.addWidget(self.status_label)

        # Butonlar oluştur
        for i in range(len(self.goals)):
            button = QPushButton(f"Hedef {i + 1}")
            button.clicked.connect(lambda _, idx=i: self.set_goal(idx))
            layout.addWidget(button)

        self.window.setLayout(layout)
        self.window.show()

    def set_goal(self, index):
        if index < len(self.goals):
            self.current_goal_index = index
            self.set_next_goal()

    def set_next_goal(self):
        if self.current_goal_index is not None:
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
            self.log_message(f"Hedef gönderiliyor: x={x}, y={y}")
            self.goal_pub.publish(goal)

    def goal_status_callback(self, msg):
        if msg.status.status == 3:  # Hedefe ulaşıldı durumu
            self.log_message(f"Hedefe ulaşıldı: {self.goals[self.current_goal_index]}")
            self.current_goal_index = None  # Hedefe ulaşıldıktan sonra indexi sıfırla

    def log_message(self, message):
        # Log mesajını arayüzde göster
        self.status_label.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    goal_setter = GoalSetter()
    sys.exit(app.exec())

