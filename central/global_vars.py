import threading
import os
import signal
#Global Variables for Lighting
#Deals with turn signal and brake lighting
turn = 0
kill_light_thread = threading.Event()

#Global Variables for Communication
kill_comm_thread = threading.Event()

#Global Variables for Braking detection
brake = 0
kill_accel_thread = threading.Event()

#Gloabel Variables for Haptic Feedback
haptic = 0
kill_distance_thread = 0

distance_mode = 0

lidar_proc = None

def kill_all_threads():
    kill_light_thread.set()
    kill_comm_thread.set()
    kill_accel_thread.set()
    lidar_proc.terminate()


    
