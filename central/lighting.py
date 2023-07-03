import time
from rpi_ws281x import *
import argparse
 
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
 
# Light the whole panel red
def brake_lights_on(strip):
    for i in range(88):
        strip.setPixelColor(i, Color(255, 0, 0, 0))
    strip.show()
 
# Turn of all the lights
def lights_off(strip):
    strip.setPixelColor(i, Color(0, 0, 0, 0))
 
# Light the right or left side of the panel (arrow), backdrop yellow
def signal_on(strip, direction):
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
 
# Main program logic follows:
 
if __name__ == '__main__':
    # TODO: Move this main functionality to central/main.py
        # For this we will have to get our turn signal and brake light exit conditions so
        # we can run an while loop for the lights
 
 
    # Process arguments
 
    parser = argparse.ArgumentParser()
 
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
 
    args = parser.parse_args()
 
    # Create NeoPixel object with appropriate configuration.
 
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
 
    # Intialize the library (must be called once before other functions).
 
    strip.begin()
 
    print ('Press Ctrl-C to quit.')
 
    if not args.clear:
 
        print('Use "-c" argument to clear LEDs on exit')
 
    try:
        while True:
            #signal_on(strip, "LEFT")
            brake_lights_on(strip)
 
    except KeyboardInterrupt:
 
        if args.clear:
 
            colorWipe(strip, Color(0,0,0), 10)