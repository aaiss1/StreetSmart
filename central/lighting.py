import time
from rpi_ws281x import *
import argparse
import global_vars
 
LED_COUNT      = 88    
LED_PIN        = 18      
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = True   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
 
 
# Hard-coded the indexes of each light on the panel based on our "snake" solder pattern
LEFT_LEDS_TOP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
LEFT_LEDS_BOT = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
RIGHT_LEDS_TOP = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
RIGHT_LEDS_BOT = [55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]
 
ARROW_LEFT = [43, 44, 3, 84, 2, 85, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]
ARROW_RIGHT = [22, 65, 23, 64, 18, 19, 68, 69, 24, 25, 26, 27, 28, 29, 30, 31, 32, 55, 56, 57, 58, 59, 60, 61, 62, 63]
 
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# Light the whole panel red
def brake_lights_on():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(255, 0, 0, 0))
    strip.show()
 
# Turn of all the lights
def lights_off():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0, 0))
    strip.show()
 
# Light the right or left side of the panel red (arrow), backdrop yellow
def signal_on(direction):
    arrow = ARROW_LEFT
 
    if direction == "RIGHT":
        arrow = ARROW_RIGHT
 
    for i in range(88):
        strip.setPixelColor(i, Color(255, 70, 0, 0))
 
    strip.show()
    time.sleep(0.5)
 
    for i in arrow:
        strip.setPixelColor(i, Color(255, 0, 0, 0))
 
    strip.show()
    time.sleep(0.5)
 
    
def update_lights():
    while not global_vars.kill_light_thread.is_set():
        if(global_vars.turn == -1):
            signal_on("LEFT")
        elif(global_vars.turn == 1):
            signal_on("RIGHT")
        else:
            brake_lights_on()
    lights_off()
    print("Lights Killed")
            

# Main program logic follows:
#This section won't be running during the thread
if __name__ == '__main__':

    try:
        global_vars.turn = -1 #Allows you to test the code 
        update_lights()
 
    except KeyboardInterrupt:
        lights_off()
