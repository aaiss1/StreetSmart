import sys
import time
import threading
import global_vars
import lighting
import comm
import accel

if __name__ == "__main__":
    #Generate all the threads and run them
    lighting_thread = threading.Thread(target=lighting.update_lights)
    comm_thread = threading.Thread(target=comm.start_comm)
    accel_thread = threading.Thread(target=accel.start_accel)

    lighting_thread.start()
    comm_thread.start()
    accel_thread.start()

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Exiting...")
        global_vars.kill_all_threads()
        
        lighting_thread.join()
        comm_thread.join()
        accel_thread.join()
        sys.exit()
