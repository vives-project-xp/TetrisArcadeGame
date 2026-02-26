# RPI 5 demo
from pi5neo import Pi5Neo
import time

num_pixels = 10

# pip install pi5neo

neo = Pi5Neo('/dev/spidev0.0', num_leds=50, spi_speed_khz=800)

def set_pixel_and_wait(n):
    neo.clear_strip()
    neo.set_led_color(n, 0, 0, 0, 255)
    neo.update_strip()
    time.sleep(0.01)


def demo():
    try:
        while True:
            print("blinking...")

            for n in range(50):
                set_pixel_and_wait(n)
            for n in range(50):
                set_pixel_and_wait(49 - n)

            neo.fill_strip(255,0,0)
            neo.update_strip()
            time.sleep(1)
            
            neo.fill_strip(0,255,0)
            neo.update_strip()
            time.sleep(1)

            neo.fill_strip(0,0,255)
            neo.update_strip()
            time.sleep(1)

            neo.fill_strip(255,255,255)
            neo.update_strip()
            time.sleep(1)

    except KeyboardInterrupt:
        neo.fill_strip(0,0,0)
        neo.update_strip()

if __name__ == "__main__":
    demo()
