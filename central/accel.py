import smbus					#import SMBus module of I2C
from time import sleep          #import
import math
import global_vars
import threading
import numpy
import time


timer_running = 0

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# Threshold values - we will have to experimentally tune these
Z_ACCEL_THRES = -0.3
Z_AVG_THRES_MIN = 0.3
Z_AVG_THRES_MAX = 0.8
TIME_FILTER_THRES = 0.02
LIGHT_OFF_DELAY = 2

 
#Helper function which calculates magnitude
def mag(x): 
    return math.sqrt(sum(i**2 for i in x))

def brake_light_off(): 
    global_vars.brake = 0
    timer_running = 0
    timer.cancel()


def MPU_Init():
	#Write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

timer = threading.Timer(LIGHT_OFF_DELAY, brake_light_off)

def start_accel():
	global timer_running
	z_moving_avg = [0]*50
	# y_moving_avg = [0]*50
	# x_moving_avg = [1]*50
	filter_timer = 0

	while not global_vars.kill_accel_thread.is_set():
		
		#Read Accelerometer raw value
		acc_x = read_raw_data(ACCEL_XOUT_H)
		acc_y = read_raw_data(ACCEL_YOUT_H)
		acc_z = read_raw_data(ACCEL_ZOUT_H)
		
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0

		# If thresh conditions are met, turn on the light
		avg_z = numpy.mean(z_moving_avg)
		# avg_y = numpy.mean(y_moving_avg)
		# avg_x = numpy.mean(x_moving_avg)
		delta = abs(avg_z - Az)
		if delta > Z_AVG_THRES_MIN and delta < Z_AVG_THRES_MAX and Ax < 1.25 and Ax > 0.75 and Ay < 0.3 and Ay > -0.3:
			if filter_timer == 0:
				filter_timer = time.time()
			else:
				t_delta = time.time() - filter_timer
				
				if t_delta > TIME_FILTER_THRES:
					print("HELLO", t_delta)
					global_vars.brake = 1
					filter_timer = 0
					if timer_running:
						timer.cancel()
						timer_running = 0
		elif global_vars.brake == 1 and timer_running == 0:  # If thresh conditions aren't met and lights are on, turn off after a delay
			timer_running = 1
			timer = threading.Timer(LIGHT_OFF_DELAY, brake_light_off)
			timer.start()
		else:
			filter_timer = 0

		print (Az, "\t", avg_z, "\t", Ay, "\t", Ax)
		z_moving_avg.pop()
		z_moving_avg.insert(0, Az)
		# y_moving_avg.pop()
		# y_moving_avg.insert(0, Ay)
		# x_moving_avg.pop()
		# x_moving_avg.insert(0, Ax)
		 	
		# sleep(0.1)
	print("Accel Killed")
