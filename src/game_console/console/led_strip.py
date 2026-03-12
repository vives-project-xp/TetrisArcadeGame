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
        self.strip = None
    
    def init_hardware(self) -> None:
        """Initialize the LED strip hardware (rpi_ws281x library)."""
        pin = getattr(board, f"D{self.__gpio_pin}")
        self.strip = neopixel.NeoPixel(
            pin, 
            self.__length, 
            pixel_order='GRBW', 
            auto_write=False
        )

        self.strip.fill(0)
        self.strip.show()

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
            self.strip._cleanup()
            self.strip = None