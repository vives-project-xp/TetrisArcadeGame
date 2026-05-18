import random
import time

import board
import neopixel

PIXEL_COUNT = 225

LED_DATA_PIN = board.D10

pixels = neopixel.NeoPixel(LED_DATA_PIN, PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
pixels.fill(0)
pixels.show()

color = (50, 50, 50)

def demo():
    pixels.fill(0)
    time.sleep(1)
    while True:
	    pixels.fill(color)
	    pixels.show()
	    time.sleep(0.2)
    pixels.fill(0)
    pixels.show()

if __name__ == "__main__":
    demo()
