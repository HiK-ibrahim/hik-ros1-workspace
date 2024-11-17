import numpy as np
from get_odom import get_current_position, get_current_angle

visited_waypoints = []  # Geçilen waypoint'leri tutacak liste
last_index = -1  # Henüz hiçbir waypoint'e ulaşılmadıysa -1 ile başlar


def load_waypoints(file_path):
    """
    Waypoints dosyasını yükle ve indeksli bir dict döndür.
    """
    waypoints = {}
    try:
        with open(file_path, 'r') as f:
            for index, line in enumerate(f):
                x, y = map(float, line.strip().split(','))
                waypoints[index] = (x, y)
    except FileNotFoundError:
        rospy.logwarn("Waypoints dosyası bulunamadı!")
        waypoints = None
    return waypoints


def find_closest_waypoint(current_position, waypoints, last_index):
    """
    Mevcut konuma en yakın ve daha önce ziyaret edilmemiş sıradaki waypoint'i bul.
    """
    min_distance = float('inf')
    closest_point = None
    closest_index = None

    for index, point in waypoints.items():
        # Eğer waypoint sırası last_index'ten büyükse (sıradaki waypoint'e bak)
        if index > last_index:
            distance = np.linalg.norm(np.array(point) - np.array(current_position))
            if distance < min_distance:
                min_distance = distance
                closest_point = point
                closest_index = index

    return closest_point, closest_index  # En yakın noktayı ve indeksini döndür


def calculate_frenet_path(line_follower, waypoints):
    """
    Frenet algoritması ile en yakın waypoint'e doğru hareket et.
    """
    global last_index  # Son indeksi global olarak kullan

    current_position = get_current_position()  # Odometri verisinden robotun pozisyonunu al
    closest_point, closest_index = find_closest_waypoint(current_position, waypoints, last_index)

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
            last_index = closest_index  # Son indeks güncellenir
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
