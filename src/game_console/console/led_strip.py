from typing import List, Tuple
import neopixel


class LEDStrip:
    """Driver for LED strip"""
    
    def __init__(self, length: int, gpio_pin) -> None:
        """
        Initialize LED strip.
        Args:
            length: led strip length
            gpio_pin: GPIO pin for data line
        """
        self.__length = length
        self._init_hardware(gpio_pin)
    
    def _init_hardware(self, gpio_pin) -> None:
        """Initialize the LED strip hardware."""
        self.__strip = neopixel.NeoPixel(
            gpio_pin,
            self.__length, 
            pixel_order='GRBW', 
            auto_write=False
        )

        self.clear()

    def clear(self) -> None:
        """Turn off all LEDs."""
        if self.__strip:
            self.__strip.fill(0)
            self.__strip.show()
    
    def set_pixel(self, i: int, color: Tuple[int, int, int]) -> None:
        """
        Set a single pixel color.
        
        Args:
            i: coordinate
            color: RGB tuple
        """
        if self.__strip and 0 <= i < self.__length:
            self.__strip[i] = color

    def show(self) -> None:
        """Update the LED strip to show changes."""
        if self.__strip:
            self.__strip.show()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.__strip:
            self.__strip.deinit()
            self.__strip = None

    def fill(self, color: Tuple[int, int, int]) -> None:
        """
        Fill the LED strip with a colors.
        
        Args:
            color: RGB tuple for each pixel
        """
        if self.__strip:
            self.__strip.fill(color)