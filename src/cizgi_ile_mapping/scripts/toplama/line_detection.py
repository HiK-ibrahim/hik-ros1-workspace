import rospy
import cv2
import numpy as np
import time

def follow_line(line_follower, image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)

    h, w = mask.shape
    search_top = 3 * h // 5
    mask[0:search_top, 0:w] = 0
    M = cv2.moments(mask)

    if M['m00'] > 0:
        cx = int(M['m10'] / M['m00'])
        err = cx - w / 2
        line_follower.twist.linear.x = 0.2
        line_follower.twist.angular.z = -float(err) / 500
        line_follower.cmd_vel_pub.publish(line_follower.twist)
        line_follower.searching = False
    else:
        search_for_line(line_follower)

def search_for_line(line_follower):
    if not line_follower.searching:
        line_follower.searching = True
        line_follower.search_start_time = time.time()
        line_follower.current_angle = 0
        line_follower.search_direction = 1
        line_follower.direction_switched = False
    else:
        if not line_follower.direction_switched:
            line_follower.twist.linear.x = 0.0
            line_follower.twist.angular.z = 0.3 * line_follower.search_direction
            line_follower.cmd_vel_pub.publish(line_follower.twist)
            line_follower.current_angle += abs(line_follower.twist.angular.z)

            if line_follower.current_angle >= 75:
                line_follower.direction_switched = True
                line_follower.current_angle = 0
        else:
            line_follower.twist.angular.z = -0.3 * line_follower.search_direction
            line_follower.cmd_vel_pub.publish(line_follower.twist)
            line_follower.current_angle += abs(line_follower.twist.angular.z)

            if line_follower.current_angle >= 150:
                line_follower.search_direction *= -1
                line_follower.direction_switched = False
                line_follower.current_angle = 0

