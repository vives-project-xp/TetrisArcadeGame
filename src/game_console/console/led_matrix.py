from typing import List, Tuple


class LEDMatrix:
    """Driver for LED strip matrix"""
    
    def __init__(self, width: int, height: int, gpio_pin: int) -> None:
        """
        Initialize LED matrix.
        
        Args:
            width: Matrix width (number of LEDs)
            height: Matrix height (number of LEDs)
            gpio_pin: GPIO pin for data line (default: 18 for PWM)
        """
        pass
    
    def init_hardware(self) -> None:
        """Initialize the LED strip hardware (rpi_ws281x library)."""
        pass
    
    def clear(self) -> None:
        """Turn off all LEDs."""
        pass

    def matrix_to_linear(self, x: int, y: int) -> int:
        """
        Translates coordinates from matrix to linear form.

        Args:
            x: X coordinate in matrix form
            y: Y coordinate in matrix form
        
        Returns:
            Coordinate in linear form
        """
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """
        Set a single pixel color.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: RGB tuple
        """
        pass
    
    def draw(self, rgbll: List[List[Tuple[int, int, int]]]) -> None:
        """
        Draw the entire matrix from a 2D list.
        
        Args:
            rgbll: 2D list [height][width] of RGB tuples
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pass