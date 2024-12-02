import rospy
import cv2
import tf2_ros
import numpy as np
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge
from geometry_msgs.msg import PointStamped
from tf2_geometry_msgs import do_transform_point

# Global değişkenler
bridge = CvBridge()
tf_buffer = None
last_lidar_msg = None  # Lidar mesajlarını saklamak için global değişken

# Kamera parametreleri
res_x = 640  # Kameranın çözünürlüğü (x)
res_y = 480  # Kameranın çözünürlüğü (y)
hfov_deg = 90  # Kameranın yatay görüş açısı (derece)

# Kamera matrisini hesapla
hfov_rad = np.deg2rad(hfov_deg)  # HFOV'u radyana çevir
f_x = res_x / (2 * np.tan(hfov_rad / 2))  # Odak uzaklığı (x)
f_y = f_x  # Odak uzaklığı (y)
c_x = res_x / 2  # Optik merkez (x)
c_y = res_y / 2  # Optik merkez (y)

camera_matrix = np.array([
    [f_x, 0, c_x],
    [0, f_y, c_y],
    [0, 0, 1]
])

dist_coeffs = np.zeros((5, 1))  # Varsayılan olarak sıfır distorsiyon katsayıları

def lidar_callback(scan):
    global tf_buffer
    try:
        # Lidar frame'inden kamera frame'ine dönüşümü al
        transform = tf_buffer.lookup_transform("front_cam_optical_frame", "laser0_frame", rospy.Time(0), rospy.Duration(1.0))
        points = []

        # Lidar verilerini işle
        angle_min = scan.angle_min
        angle_increment = scan.angle_increment
        for i, r in enumerate(scan.ranges):
            if r > scan.range_min and r < scan.range_max:
                angle = angle_min + i * angle_increment
                # Lidar polar verisini Kartezyen'e çevir
                x = r * np.cos(angle)
                y = r * np.sin(angle)
                z = 0.0  # Z düzleminde lidar noktası

                # Kamera frame'ine dönüştür
                point = PointStamped()
                point.header = scan.header
                point.point.x = x
                point.point.y = y
                point.point.z = z
                transformed_point = do_transform_point(point, transform)

                points.append((transformed_point.point.x, transformed_point.point.y, transformed_point.point.z))

        return points
    except tf2_ros.TransformException as ex:
        rospy.logwarn(f"Transform hatası: {ex}")
        return []

def camera_callback(image_msg):
    global last_lidar_msg
    try:
        if last_lidar_msg is None:
            return  # Eğer lidar mesajı yoksa geri dön

        # Kameradan gelen görüntüyü OpenCV formatına çevir
        cv_image = bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
        lidar_points = lidar_callback(last_lidar_msg)  # Son lidar mesajını kullan
        for point in lidar_points:
            # Kamera frame'indeki noktaları piksel koordinatına projelendir
            x, y, z = point
            pixel = camera_matrix @ np.array([x, y, z])
            pixel = pixel / pixel[2]  # Homojen koordinatları normalize et
            cv2.circle(cv_image, (int(pixel[0]), int(pixel[1])), 5, (0, 255, 0), -1)

        # Görüntüyü ekrana bastır
        cv2.imshow("Camera with Lidar", cv_image)
        cv2.waitKey(1)
    except Exception as ex:
        rospy.logwarn(f"Kamera işlem hatası: {ex}")

if __name__ == "__main__":
    rospy.init_node("lidar_camera_fusion")

    # TF listener ayarı
    tf_buffer = tf2_ros.Buffer()
    tf_listener = tf2_ros.TransformListener(tf_buffer)

    # Lidar ve kamera abone ayarları
    rospy.Subscriber("/scan", LaserScan, lambda msg: globals().update(last_lidar_msg=msg))
    rospy.Subscriber("/front_cam/camera/image", Image, camera_callback)

    rospy.spin()
    cv2.destroyAllWindows()