import board
import neopixel
import time

GPIO_PIN = board.D24  # Example usage of GPIO pin 24
NUM_OF_LEDS = 88  # We have 88 LEDs on the panel 

# Hard-coded the indexes of each light on the panel based on our "snake" solder pattern
LEFT_LEDS_TOP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
LEFT_LEDS_BOT = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
RIGHT_LEDS_TOP = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
RIGHT_LEDS_BOT = [55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]

# Light the whole panel red
def brake_lights_on(pixels):
    pixels.fill((255, 0, 0))

# Turn of all the lights
def lights_off(pixels):
    pixels.fill((0, 0, 0))

# Light the right or left side of the panel
def signal_on(pixels, direction):
    top = LEFT_LEDS_TOP
    bottom = LEFT_LEDS_BOT

    if direction == "RIGHT":
        top = RIGHT_LEDS_TOP
        bottom = RIGHT_LEDS_BOT
    
    for i in top:
        pixels[i] = (255, 255, 0)  # Light the top quarter yellow
    for i in bottom:
        pixels[i] = (255, 0, 0)  # Light the bottom quarter red

# TODO: Add this to central/main.py
pixels = neopixel.NeoPixel(GPIO_PIN, NUM_OF_LEDS)  # Initial pixels array setup