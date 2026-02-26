import time

import board
import neopixel_spi

PIXEL_COUNT = 300
SNAKE_LEN = 10

pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
pixels.fill(0)
# it glitches more without the pixels.show()
# pixels.show()

def set_pixels_and_wait(n, color):
    pixels.fill(0)
    pixels[n:n+SNAKE_LEN] = [color] * SNAKE_LEN
    pixels.show()
    time.sleep(0.005)
    # time.sleep(0.5)

def demo():
    try:
        while True:
            time.sleep(1)
            print("blinking...")

            colors = [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 255)
            ]

            for color in colors:

                for n in range(PIXEL_COUNT - SNAKE_LEN):
                    set_pixels_and_wait(n, color)
                pixels.fill(0)
                pixels.show()
                for n in range(PIXEL_COUNT):
                    set_pixels_and_wait(PIXEL_COUNT  - SNAKE_LEN - 1 - n, color)

    except KeyboardInterrupt:
        pixels.fill(0)
        pixels.show()

if __name__ == "__main__":
    demo()