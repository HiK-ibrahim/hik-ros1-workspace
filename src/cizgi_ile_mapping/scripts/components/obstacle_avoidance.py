import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import time

class ObstacleAvoidance:
    def __init__(self, cmd_vel_topic="/cmd_vel", scan_topic="/scan"):
        self.cmd_vel_pub = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)
        self.scan_sub = rospy.Subscriber(scan_topic, LaserScan, self.scan_callback)
        self.twist = Twist()
        self.obstacle_detected = False
        self.avoidance_mode = False
        self.rate = rospy.Rate(10)  # 10 Hz döngü hızı
        self.front_clear = True

    def scan_callback(self, scan):
        """
        Lidar verilerini kontrol et ve engel varsa engel tespitini yap.
        """
        try:
            # Ön bölge taraması (360-0 derece birleştirilmiş)
            on = min(scan.ranges[350:360] + scan.ranges[0:10])
            distance_threshold = 0.6  # Engel algılama eşiği (metre)

            self.front_clear = on >= distance_threshold

            if not self.front_clear:
                rospy.loginfo("Ön bölgede engel var!")
                self.obstacle_detected = True
            else:
                self.obstacle_detected = False
        except ValueError:
            rospy.logwarn("Lidar verisi boş veya geçersiz!")
            self.front_clear = False

    def move_in_curve_until_clear(self, direction, forward_speed=0.05, turn_speed=1.4):
        """
        Robotu önünde engel kalmayana kadar kavisli bir şekilde hareket ettir.
        """
        self.twist.linear.x = forward_speed
        self.twist.angular.z = turn_speed if direction == "right" else -turn_speed

        rospy.loginfo(f"{direction.capitalize()} yönünde kavisli dönüş yapılıyor...")
        while not self.front_clear and not rospy.is_shutdown():
            self.cmd_vel_pub.publish(self.twist)
            self.rate.sleep()

        # Hareketi durdur
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist)

    def avoid_obstacle(self):
        """
        Engel algılama ve kaçınma işlemi.
        """
        if self.obstacle_detected:
            self.avoidance_mode = True
            rospy.loginfo("Engel tespit edildi, kaçınılıyor...")

            # 1. Kavisli dönüş: Sağa dönerek engelden uzaklaş
            rospy.loginfo("Sola kavisli dönüş yapılıyor...")
            self.move_in_curve_until_clear("right")

            # 2. Düz ilerleme
            rospy.loginfo("Engelden uzaklaşılıyor, düz ilerleniyor...")
            self.move_forward(duration=5)


            # 3. Ters kavisli dönüş: Rotaya geri dön
            rospy.loginfo("Sola kavisli dönüş ile rotaya dönülüyor...")
            self.move_in_curve("left", duration=4)

        self.avoidance_mode = False

    def move_forward(self, duration, speed=0.2):
        """
        Robotu belirli bir süre ileri hareket ettir.
        """
        self.twist.linear.x = speed
        self.twist.angular.z = 0.0
        start_time = time.time()

        while time.time() - start_time < duration and not rospy.is_shutdown():
            self.cmd_vel_pub.publish(self.twist)
            self.rate.sleep()

        self.twist.linear.x = 0.0
        self.cmd_vel_pub.publish(self.twist)

    def is_avoiding_obstacle(self):
        """
        Engel kaçınma işlemi sırasında aktifse True döner, aksi takdirde False.
        """
        return self.avoidance_mode

    def move_in_curve(self, direction, duration, forward_speed=0.15, turn_speed=0.4):
        """
        Robotu kavisli bir şekilde hareket ettir.
        """
        self.twist.linear.x = forward_speed
        self.twist.angular.z = turn_speed if direction == "right" else -turn_speed

        start_time = time.time()
        while time.time() - start_time < duration and not rospy.is_shutdown():
            self.cmd_vel_pub.publish(self.twist)
            self.rate.sleep()

        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        self.cmd_vel_pub.publish(self.twist)

    def run(self):
        """
        Engel varsa kaçınma işlemi yap, yoksa çizgi takibi moduna dön.
        """
        if self.obstacle_detected and not self.avoidance_mode:
            self.avoid_obstacle()
