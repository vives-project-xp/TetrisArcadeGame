from typing import List, Tuple
import board
import neopixel


class LEDStrip:
    """Driver for LED strip"""
    
    def __init__(self, length: int, gpio_pin: int) -> None:
        """
        Initialize LED strip.
        Args:
            length: led strip length
            gpio_pin: GPIO pin for data line
        """
        self.__length = length
        self.__gpio_pin = gpio_pin
        self.__init_hardware()
    
    def __init_hardware(self) -> None:
        """Initialize the LED strip hardware."""
        self.strip = neopixel.NeoPixel(
            self.__gpio_pin, 
            self.__length, 
            pixel_order='GRBW', 
            auto_write=False
        )

        self.clear()

    def clear(self) -> None:
        """Turn off all LEDs."""
        if self.strip:
            self.strip.fill(0)
            self.strip.show()
    
    def set_pixel(self, i: int, color: Tuple[int, int, int]) -> None:
        """
        Set a single pixel color.
        
        Args:
            i: coordinate
            color: RGB tuple
        """
        if self.strip and 0 <= i < self.__length:
            self.strip[i] = color

    def show(self) -> None:
        """Update the LED strip to show changes."""
        if self.strip:
            self.strip.show()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.strip:
            self.strip.deinit()
            self.strip = None

    def fill(self, color: Tuple[int, int, int]) -> None:
        """
        Fill the LED strip with a colors.
        
        Args:
            color: RGB tuple for each pixel
        """
        if self.strip:
            self.strip.fill(color)