import rospy
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

def get_current_position():
    """
    Odometri verilerinden robotun mevcut pozisyonunu al.
    """
    # Global değişkenlere odometri verisini dinlemek için bir subscriber ekleyelim
    global current_position
    current_position = None

    def odometry_callback(msg):
        global current_position
        current_position = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    # Odometry bilgilerini dinle
    rospy.Subscriber("/odom", Odometry, odometry_callback)

    # İlk başta current_position değerini bekle
    while current_position is None:
        rospy.sleep(0.1)

    return current_position

def get_current_angle():
    """
    Odometri verilerinden robotun mevcut yönelim açısını (yaw) al.
    """
    global current_angle
    current_angle = None

    def odometry_callback(msg):
        global current_angle
        # Quaternion'ı Euler açılarına çevir
        orientation = msg.pose.pose.orientation
        (roll, pitch, yaw) = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])
        current_angle = yaw  # Yaw açısını kullanıyoruz (dönme açısı)

    # Odometry bilgilerini dinle
    rospy.Subscriber("/odom", Odometry, odometry_callback)

    # İlk başta current_angle değerini bekle
    while current_angle is None:
        rospy.sleep(0.1)

    return current_angle
