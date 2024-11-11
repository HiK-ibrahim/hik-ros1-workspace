#!/usr/bin/env python3
import sys
import rospy
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from functools import partial

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
        self.previous_button = None  # Önceki butonu saklamak için

        # Arayüz oluştur
        self.init_ui()

    def init_ui(self):
        self.window = QWidget()
        self.window.setWindowTitle("Robot Hedef Belirleyici")
        self.window.setStyleSheet("background-color: gray;")  # Gri arka plan
        layout = QVBoxLayout()

        self.label = QLabel("Hedefler: ")
        layout.addWidget(self.label)

        self.status_label = QLabel("")  # Durum etiketini oluştur
        layout.addWidget(self.status_label)

        # Butonlar oluştur
        self.buttons = []  # Butonları saklamak için bir liste
        for i in range(len(self.goals)):
            button = QPushButton(f"Hedef {i + 1}")
            button.setStyleSheet("background-color: black; color: white;")  # Siyah arka plan ve beyaz yazı
            # `partial` kullanarak buton tıklama fonksiyonunu ayarlıyoruz
            button.clicked.connect(partial(self.set_goal, i, button))  
            layout.addWidget(button)
            self.buttons.append(button)  # Butonu listeye ekle

        self.window.setLayout(layout)
        self.window.show()

    def set_goal(self, index, button):
        if index < len(self.goals):
            # Önceki butonun rengini geri al
            if self.previous_button and self.previous_button != button:
                self.previous_button.setStyleSheet("background-color: black; color: white;")  # Eski butonu siyaha döndür
            
            self.current_goal_index = index
            button.setStyleSheet("background-color: yellow; color: black;")  # Sarı yap
            self.previous_button = button  # Mevcut butonu sakla
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
            # Hedefe ulaşıldığında butonu kırmızı yap
            if self.current_goal_index is not None:
                self.buttons[self.current_goal_index].setStyleSheet("background-color: red; color: white;")
            self.current_goal_index = None  # Hedefe ulaşıldıktan sonra indexi sıfırla

    def log_message(self, message):
        # Log mesajını arayüzde göster
        self.status_label.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    goal_setter = GoalSetter()
    sys.exit(app.exec())

