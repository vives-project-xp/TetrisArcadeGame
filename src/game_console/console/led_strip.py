from typing import List, Tuple


class LEDStrip:
    """Driver for LED strip"""
    
    def __init__(self, length: int, gpio_pin: int) -> None:
        """
        Initialize LED matrix.
        Args:
            length: led strip length
            gpio_pin: GPIO pin for data line
        """
        self.__length = length

        pass
    
    def init_hardware(self) -> None:
        """Initialize the LED strip hardware (rpi_ws281x library)."""
        pass
    
    def clear(self) -> None:
        """Turn off all LEDs."""
        pass
    
    def set_pixel(self, i: int, color: Tuple[int, int, int]) -> None:
        """
        Set a single pixel color.
        
        Args:
            i: coordinate
            color: RGB tuple
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.strip:
            self.strip._cleanup()
            self.strip = None