import sys
import time
import threading
import global_vars
import lighting
import comm
import accel
# import distance
import lidar_dist
from multiprocessing import Process, Queue, Value, ProcessError


if __name__ == "__main__":
    #Generate all the threads and run them
    lighting_thread = threading.Thread(target=lighting.update_lights)
    comm_thread = threading.Thread(target=comm.start_comm)
    accel_thread = threading.Thread(target=accel.start_accel)
    # distance_thread = threading.Thread(target=distance.start_distance)

    haptic = Value('i', 0)
    try:
        global_vars.lidar_proc = Process(target=lidar_dist.start_lidar_distance, args=(haptic, ))
        global_vars.lidar_proc.start()

        # distance_thread = threading.Thread(target=lidar_dist.start_lidar_distance)

        lighting_thread.start()
        comm_thread.start()
        accel_thread.start()
        # distance_thread.start()
        while True:
            global_vars.haptic = haptic.value
            
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Exiting...")
        
        global_vars.kill_all_threads()
  
        lighting_thread.join()
        comm_thread.join()
        accel_thread.join()
        # distance_thread.join()
        global_vars.lidar_proc.join()

        
        sys.exit()
