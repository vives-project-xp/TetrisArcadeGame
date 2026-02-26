import time

import board
import neopixel_spi
import RPi.GPIO as GPIO

PIXEL_COUNT = 50
DOT_COLOR = (0, 0, 255)
BTN_LEFT_PIN = 26
BTN_RIGHT_PIN = 20

pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), PIXEL_COUNT, pixel_order='GRBW', auto_write=False)
dot_loc = PIXEL_COUNT // 2

def refresh_dot():
    pixels.fill(0)
    pixels[dot_loc] = DOT_COLOR
    pixels.show()
    print("The location is ", dot_loc)

def move_dot_left():
    global dot_loc
    dot_loc -= 1
    if (dot_loc < 0):
        dot_loc = PIXEL_COUNT - 1
    refresh_dot()

def move_dot_right():
    global dot_loc
    dot_loc += 1
    if (dot_loc >= PIXEL_COUNT):
        dot_loc = 0
    refresh_dot()

def demo():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)
    GPIO.setup(BTN_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    pixels.fill(0)
    pixels.show()
    # GPIO.wait_for_edge(BTN_LEFT_PIN, GPIO.FALLING)
    # GPIO.add_event_detect(BTN_LEFT_PIN, GPIO.FALLING)
    # GPIO.add_event_detect(BTN_RIGHT_PIN, GPIO.FALLING, callback=move_dot_right, bouncetime=100)
    refresh_dot()

    try:

        print("Running... Press Ctrl+C to exit")
        while True:
            if GPIO.input(BTN_LEFT_PIN) == GPIO.LOW:
                move_dot_left()
            if GPIO.input(BTN_RIGHT_PIN) == GPIO.LOW:
                move_dot_right()
            time.sleep(0.01)

    except KeyboardInterrupt:
        pixels.deinit()
        GPIO.cleanup()

if __name__ == "__main__":
    # time.sleep(1)
    demo()