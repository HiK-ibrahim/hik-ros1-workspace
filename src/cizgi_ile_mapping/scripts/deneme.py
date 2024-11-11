#!/usr/bin/env python

import subprocess
import rospy
import os

def run_map_saver():
    # Map kaydetme komutunu oluştur
    map_save_command = "rosrun map_server map_saver -f /home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/slam_ve_navigation/map/gmapping/cizgiVEqrMap"
    
    # subprocess ile xterm'de çalıştırma
    process = subprocess.Popen(['xterm', '-hold', '-e', map_save_command])
    



if __name__ == "__main__":
    rospy.init_node('map_saver_runner')
    run_map_saver()

