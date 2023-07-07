import sys
import time
import threading
import global_vars
import lighting
import comm
import signal

if __name__ == "__main__":
    #Generate all the threads and run them
    lighting_thread = threading.Thread(target=lighting.update_lights)
    comm_thread = threading.Thread(target=comm.start_comm)
    lighting_thread.start()
    comm_thread.start()

    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Exiting...")
        global_vars.kill_all_threads()
        
        lighting_thread.join()
        comm_thread.join()
        
        sys.exit()
