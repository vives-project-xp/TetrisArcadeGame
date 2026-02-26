import time

import board
import neopixel_spi

PIXEL_COUNT = 127


def demo():
    pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
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