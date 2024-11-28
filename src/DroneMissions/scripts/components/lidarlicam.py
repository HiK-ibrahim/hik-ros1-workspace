import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, LaserScan
import tf

class LidarCameraOverlay:
    def __init__(self):
        rospy.init_node('lidar_camera_overlay', anonymous=True)

        # Kameradan gelen görüntü için subscriber
        self.image_sub = rospy.Subscriber('/front_cam/camera/image', Image, self.image_callback)
        
        # LIDAR verisi için subscriber
        self.lidar_sub = rospy.Subscriber('/scan', LaserScan, self.lidar_callback)

        # TF Listener: Çerçeve dönüşümü yapmak için
        self.tf_listener = tf.TransformListener()

        # CV Bridge: ROS mesajlarını OpenCV formatına dönüştürmek için
        self.bridge = CvBridge()

        # Veri depolamak için
        self.current_image = None
        self.lidar_data = None
        self.lidar_angle_increment = None
        self.lidar_min_angle = None

        # Çerçeve adları
        self.lidar_frame = "laser0_frame"  # LIDAR çerçevesi
        self.camera_frame = "front_cam_optical_frame"  # Kamera çerçevesi

    def image_callback(self, msg):
        """Kameradan gelen görüntüyü kaydet"""
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr(f"Image callback error: {e}")

    def lidar_callback(self, msg):
        """LIDAR verisini kaydet"""
        self.lidar_data = np.array(msg.ranges)
        self.lidar_angle_increment = msg.angle_increment
        self.lidar_min_angle = msg.angle_min

    def overlay_lidar_on_image(self):
        """Görüntünün üzerine LIDAR verisini bindir"""
        if self.current_image is None or self.lidar_data is None:
            return

        try:
            # LIDAR'dan kamera çerçevesine dönüşüm matrisi al
            trans, rot = self.tf_listener.lookupTransform(self.camera_frame, self.lidar_frame, rospy.Time(0))
            rotation_matrix = tf.transformations.quaternion_matrix(rot)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.logwarn(f"TF error: {e}")
            return

        # Görüntü boyutlarını al
        height, width, _ = self.current_image.shape
        center_x, center_y = width // 2, height // 2  # Görüntünün merkezi

        # LIDAR verilerini görüntü üzerine ekle
        for i, distance in enumerate(self.lidar_data):
            if not np.isfinite(distance):  # Geçersiz mesafeleri atla
                continue

            # LIDAR noktasını LIDAR çerçevesinde hesapla
            angle = self.lidar_min_angle + i * self.lidar_angle_increment
            lidar_point = np.array([distance * np.cos(angle), distance * np.sin(angle), 0, 1])  # Homojen koordinatlar

            # LIDAR noktasını kamera çerçevesine dönüştür
            camera_point = np.dot(rotation_matrix, lidar_point)
            x, y, _ = camera_point[:3]  # Z ekseni göz ardı edilebilir

            # Görüntü piksel koordinatlarına dönüştür
            pixel_x = int(center_x + x * 100)  # Görselleştirme için ölçek
            pixel_y = int(center_y - y * -100)  # Y koordinatı terstir

            # Görüntü sınırları içinde mi kontrol et
            if 0 <= pixel_x < width and 0 <= pixel_y < height:
                # LIDAR noktalarını çizin
                cv2.circle(self.current_image, (pixel_x, pixel_y), 2, (0, 255, 0), -1)  # Kırmızı noktalar

        # Görüntüyü göster
        cv2.imshow("Lidar-Camera Overlay", self.current_image)
        cv2.waitKey(1)

    def run(self):
        """ROS döngüsü"""
        rate = rospy.Rate(10)  # 10 Hz
        while not rospy.is_shutdown():
            self.overlay_lidar_on_image()
            rate.sleep()


if __name__ == "__main__":
    node = LidarCameraOverlay()
    try:
        node.run()
    except rospy.ROSInterruptException:
        pass

