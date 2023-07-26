import sys
import time
import threading
import global_vars
import lighting
import comm
import accel
import distance

if __name__ == "__main__":
    #Generate all the threads and run them
    lighting_thread = threading.Thread(target=lighting.update_lights)
    comm_thread = threading.Thread(target=comm.start_comm)
    accel_thread = threading.Thread(target=accel.start_accel)
    distance_thread = threading.Thread(target=distance.start_distance)

    lighting_thread.start()
    comm_thread.start()
    accel_thread.start()
    time.sleep(5)
    distance_thread.start()

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Exiting...")
        global_vars.kill_all_threads()
        
        lighting_thread.join()
        comm_thread.join()
        accel_thread.join()
        distance_thread.join()
        
        sys.exit()
