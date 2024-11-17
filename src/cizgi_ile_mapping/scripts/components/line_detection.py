import rospy
import cv2
import numpy as np
import time
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion  # Quaternion -> Euler dönüşümü için
import time
#Çizgi kaybolduğunda bekleme süresi (saniye cinsinden)
LINE_LOST_TIMEOUT = 0.5  # 2 saniye boyunca çizgiyi bulmaya çalış

def follow_line(line_follower, image):
    """
    Çizgiyi takip et ve waypoint'lere göre Frenet algoritmasıyla ya da çizgi arama modunda devam et.
    """
    # HSV renk uzayında kırmızı renk maskesi oluştur
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Kırmızı rengin HSV aralığı
    lower_red = np.array([0, 50, 50])  # Düşük kırmızı tonları
    upper_red = np.array([10, 255, 255])  # Yüksek kırmızı tonları

    # Diğer kırmızı tonlarını da kapsamak için
    lower_red2 = np.array([170, 50, 50])  # Kırmızı rengin diğer tonları
    upper_red2 = np.array([180, 255, 255])  # Yüksek kırmızı tonları

    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # İki maskeyi birleştiriyoruz
    mask = cv2.bitwise_or(mask1, mask2)

    # Waypoints'i yükle (otomatik olarak dosya yolunu kontrol eder)
    waypoints = load_waypoints('/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/cizgi_ile_mapping/scripts/components/waypoints.txt')

    # Maskenin üst kısmını göz ardı et
    h, w = mask.shape
    search_top = 3 * h // 5
    mask[0:search_top, 0:w] = 0
    M = cv2.moments(mask)

    if M['m00'] > 0:
        # Çizgiyi tespit ettik, takip et
        cx = int(M['m10'] / M['m00'])
        err = cx - w / 2

        # Dönüş hızını daha yumuşak yap
        angular_velocity = -float(err) / 1000  # 500 yerine 1000 ile daha az hassasiyet
        if abs(angular_velocity) > 0.2:  # 0.2'yi sınırlandırarak keskin dönüşleri engelle
            angular_velocity = np.sign(angular_velocity) * 0.2  # Maksimum dönüş hızı 0.2

        line_follower.twist.linear.x = 0.2  # Sabit ileri hız
        line_follower.twist.angular.z = angular_velocity
        line_follower.cmd_vel_pub.publish(line_follower.twist)

        line_follower.searching = False
        line_follower.line_lost_time = None  # Çizgi bulundu, kaybolduğunda başlatılan zamanlayıcıyı sıfırlıyoruz
    else:
        # Çizgi kaybolduğunda zamanlayıcıyı başlatıyoruz
        if not hasattr(line_follower, 'line_lost_time') or line_follower.line_lost_time is None:
            line_follower.line_lost_time = time.time()  # Zamanlayıcıyı başlat

        # Çizgi kaybolduğunda 2 saniye boyunca bekliyoruz
        if time.time() - line_follower.line_lost_time < LINE_LOST_TIMEOUT:
            print("Çizgi kayboldu, search_for_line ile çizgi aranıyor...")
            # Çizgiyi bulmaya çalış
            search_for_line(line_follower)
        else:
            if waypoints:
                print("Freenet ile çizgi bulunuyor")
                # Waypoints varsa Frenet algoritması ile devam et
                calculate_frenet_path(line_follower, waypoints)
            else:
                # Waypoints yoksa çizgi arama moduna geç
                print("Search for line algoritması ile çizgi aranıyor")
                search_for_line(line_follower)

visited_waypoints = []  # Geçilen waypoint'leri tutacak liste

def calculate_frenet_path(line_follower, waypoints):
    """
    Frenet algoritması ile en yakın waypoint'e doğru hareket et.
    """
    current_position = get_current_position()  # Odometri verisinden robotun pozisyonunu al
    closest_point = find_closest_waypoint(current_position, waypoints)

    if closest_point:
        target_angle = np.arctan2(closest_point[1] - current_position[1],
                                  closest_point[0] - current_position[0])
        current_angle = get_current_angle()  # Mevcut açıyı al

        # Hedefe olan mesafeyi hesapla
        distance_to_target = np.linalg.norm(np.array(closest_point) - np.array(current_position))

        print(f"Hedef: {closest_point}, Konum: {current_position}, Mesafe: {distance_to_target}")

        if distance_to_target < 0.2:  # Hedefe yaklaşıldığında, robot durmalı
            # Bu waypoint'i ziyaret edilmiş olarak kaydediyoruz
            visited_waypoints.append(closest_point)
            print(f"Hedefe ulaşıldı! Ziyaret edilen waypoints: {visited_waypoints}")
            line_follower.twist.linear.x = 0.0
            line_follower.twist.angular.z = 0.0
        else:
            # Açılar arasındaki farkı hesapla
            angle_diff = target_angle - current_angle
            line_follower.twist.linear.x = 0.1
            line_follower.twist.angular.z = angle_diff
            line_follower.cmd_vel_pub.publish(line_follower.twist)
    else:
        print("En yakın waypoint bulunamadı!")

def find_closest_waypoint(current_position, waypoints):
    """
    Şu anki konuma en yakın ve daha önce ziyaret edilmemiş waypoint'i bul.
    """
    min_distance = float('inf')
    closest_point = None
    for point in waypoints:
        # Eğer bu waypoint daha önce ziyaret edilmemişse
        if point not in visited_waypoints:
            distance = np.linalg.norm(np.array(point) - np.array(current_position))
            if distance < min_distance:
                min_distance = distance
                closest_point = point
    return closest_point


def load_waypoints(file_path):
    """
    Waypoints dosyasını yükle ve liste döndür.
    """
    waypoints = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                x, y = map(float, line.strip().split(','))
                waypoints.append((x, y))
    except FileNotFoundError:
        rospy.logwarn("Waypoints dosyası bulunamadı!")
        waypoints = None
    return waypoints

def search_for_line(line_follower):
    """
    Çizgiyi kaybedince arama moduna geç.
    """
    if not line_follower.searching:
        line_follower.searching = True
        line_follower.search_start_time = time.time()
        line_follower.current_angle = 0
        line_follower.search_direction = 1
        line_follower.direction_switched = False
    else:
        if not line_follower.direction_switched:
            # İlk dönüş yönü
            line_follower.twist.linear.x = 0.0
            line_follower.twist.angular.z = 0.3 * line_follower.search_direction
            line_follower.cmd_vel_pub.publish(line_follower.twist)
            line_follower.current_angle += abs(line_follower.twist.angular.z)

            if line_follower.current_angle >= 75:
                line_follower.direction_switched = True
                line_follower.current_angle = 0
        else:
            # Karşı dönüş yönü
            line_follower.twist.angular.z = -0.3 * line_follower.search_direction
            line_follower.cmd_vel_pub.publish(line_follower.twist)
            line_follower.current_angle += abs(line_follower.twist.angular.z)

            if line_follower.current_angle >= 150:
                line_follower.search_direction *= -1
                line_follower.direction_switched = False
                line_follower.current_angle = 0

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