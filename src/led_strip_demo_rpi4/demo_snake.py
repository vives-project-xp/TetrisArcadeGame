import random
import time

import board
import neopixel

PIXEL_COUNT = 20
SNAKE_LEN = 2

LED_DATA_PIN = board.D10

pixels = neopixel.NeoPixel(LED_DATA_PIN, PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
pixels.fill(0)
pixels.show()

color = (100, 100, 100)

target_fps = 15
frame_duration = 1.0 / target_fps
last_time = time.perf_counter()

def update_pixels(n):
    pixels.fill(0)
    new_value = []
    global color
    for i in range(3):
        new_value.append(color[i])
        new_value[i] += random.randint(0, 30) - 15
        new_value[i] = min(255, max(0, new_value[i]))
    color = (new_value[0], new_value[1], new_value[2])
    pixels[n:n+SNAKE_LEN] = [color] * SNAKE_LEN
    pixels.show()

def demo():
    try:
        n = 0
        up = True
        while True:
            current_time = time.perf_counter()
            global last_time
            delta = current_time - last_time
            
            print(1/delta)
            if delta >= frame_duration:
                update_pixels(n)
                if up:
                    n = n + 1
                    if n == (PIXEL_COUNT - SNAKE_LEN):
                        up = False
                elif up == False:
                    n = n - 1
                    if n == 0:
                        up = True
                last_time = current_time

    except KeyboardInterrupt:
        pixels.fill(0)
        pixels.show()

if __name__ == "__main__":
    demo()
