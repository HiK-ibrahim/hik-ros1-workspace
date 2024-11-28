#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist  # Hareket komutları için

class TakeoffControl:
    def __init__(self):
        # Hareket komutları için publisher
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rospy.sleep(1)  # Publisher'ın aktifleşmesi için kısa bekleme

    def takeoff(self):
        """
        Drone'u 1 metreye kaldırır ve sabit tutar.
        """
        rospy.loginfo("Kalkış başlıyor...")
        takeoff_cmd = Twist()

        # Yukarıya doğru hız (z ekseni)
        takeoff_cmd.linear.z = 1.0  # 1 m/s hızla kalkış

        # Komutu birkaç saniye yayınla
        rate = rospy.Rate(10)  # 10 Hz
        for _ in range(10):  # 1 saniye boyunca yayın
            self.cmd_vel_pub.publish(takeoff_cmd)
            rate.sleep()

        # Hızı sıfırlayarak sabit tut
        hover_cmd = Twist()  # Tüm hızlar 0
        self.cmd_vel_pub.publish(hover_cmd)
        rospy.loginfo("Drone 1 metreye ulaştı ve sabit duruyor.")

if __name__ == "__main__":
    rospy.init_node('takeoff_control', anonymous=True)

    takeoff_control = TakeoffControl()
    takeoff_control.takeoff()

