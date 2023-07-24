import threading
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
kill_distance_thread = threading.Event()


def kill_all_threads():
    kill_light_thread.set()
    kill_comm_thread.set()
    kill_accel_thread.set()
    kill_distance_thread.set()
