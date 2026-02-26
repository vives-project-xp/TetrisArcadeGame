import time

import board
import neopixel

PIXEL_COUNT = 127


def demo():
    pixels = neopixel.NeoPixel(board.PWM0, PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
    pixels.fill(0)
    pixels[1] = (0, 0, 255)
    pixels.show()
    time.sleep(1)
    pixels[1] = (0, 0, 255)
    pixels.show()
    time.sleep(1)
    pixels.deinit()


if __name__ == "__main__":
    # time.sleep(1)
    demo()