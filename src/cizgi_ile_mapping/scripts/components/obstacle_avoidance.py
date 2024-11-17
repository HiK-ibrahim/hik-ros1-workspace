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

    def scan_callback(self, scan):
        """
        Lidar verilerini kontrol et ve engel varsa engel tespitini yap.
        """
        try:
            sag = min(scan.ranges[-10:])  # Sağ (son 10 derece)
            sol = min(scan.ranges[0:10])  # Sol (ilk 10 derece)
            on = min(scan.ranges[350:360] + scan.ranges[0:10])  # Ön (360-0 derece birleştirilmiş)

            distance_threshold = 0.7  # Engel algılama eşiği (metre)

            if on < distance_threshold or sag < distance_threshold or sol < distance_threshold:
                rospy.loginfo("Engel tespit edildi! Engel algılanıyor.")
                self.obstacle_detected = True
            else:
                self.obstacle_detected = False
        except ValueError:
            rospy.logwarn("Lidar verisi boş veya geçersiz!")
            self.obstacle_detected = False

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

    def avoid_obstacle(self):
        """
        Engel algılama ve kaçınma işlemi.
        """
        if self.obstacle_detected:
            self.avoidance_mode = True
            rospy.loginfo("Engel tespit edildi, kaçınılıyor...")

            # 1. Kavisli dönüş: Sağa dönerek engelden uzaklaş
            rospy.loginfo("Sağa kavisli dönüş yapılıyor...")
            self.move_in_curve("right", duration=2)

            # 2. Düz ilerleme
            rospy.loginfo("Engelden uzaklaşılıyor, düz ilerleniyor...")
            self.move_forward(duration=4)

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
    def run(self):
        """
        Engel varsa kaçınma işlemi yap, yoksa çizgi takibi moduna dön.
        """
        if self.obstacle_detected and not self.avoidance_mode:
            self.avoid_obstacle()


            # Burada çizgi takibi ve frenet gibi diğer algoritmalar çalıştırılabilir