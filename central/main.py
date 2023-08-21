import sys
import time
import threading
import global_vars
import lighting
import comm
import accel
# import distance
import lidar_dist
from multiprocessing import Process, Queue, Value


if __name__ == "__main__":
    #Generate all the threads and run them
    lighting_thread = threading.Thread(target=lighting.update_lights)
    comm_thread = threading.Thread(target=comm.start_comm)
    accel_thread = threading.Thread(target=accel.start_accel)
    # distance_thread = threading.Thread(target=distance.start_distance)
    q = Value('i', 0)
    p = Process(target=lidar_dist.start_lidar_distance, args=(q,))
    p.start()


    # distance_thread = threading.Thread(target=lidar_dist.start_lidar_distance)

    lighting_thread.start()
    comm_thread.start()
    accel_thread.start()
    # distance_thread.start()

    try:
        while True:
                global_vars.haptic = q.value
            
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Exiting...")
        global_vars.kill_all_threads()
        
        lighting_thread.join()
        comm_thread.join()
        accel_thread.join()
        # distance_thread.join()
        
        sys.exit()
