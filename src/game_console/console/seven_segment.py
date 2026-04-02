from typing import List, Tuple
from ht16k33 import HT16K33SegmentBig

import config
import busio
import board


class SevenSegment:
    """Driver for seven-segment display"""
    
    def __init__(self) -> None:
        """
        Initialize the display.
        """
        self.__led = None
        self.__init_hardware(config.SEVEN_SEGMENT_I2C_ADDRESS)
    
    def __init_hardware(self, i2c_address) -> None:
        """Initialize the display hardware."""
        i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        self.__led = HT16K33SegmentBig(i2c, i2c_address=i2c_address)

        self.__led.set_brightness(config.SEVEN_SEGMENT_LED_BRIGHTNESS)
    
    def set_colon(self, pattern) -> None:
        """Set which colon/point indicators are illuminated on the display.

        Bit flags:
            0x02: Centre colon
            0x04: Left colon, lower dot
            0x08: Left colon, upper dot
            0x10: Decimal point (upper)

        Args:
            pattern (int): Integer bitfield specifying which indicators to light.

        Example:
            # Set the centre : and the left :
            pattern = 0x02 | 0x04 | 0x08
        """
        self.__led.set_colon(pattern)

    def print_string(self, stringToPrint: str, alighRight : bool = False) -> None:
        """
        Print a string on the seven-segment display.

        Supported symbols: 0-9, A-F, '-', ' ', and degree ('deg' or '°').
        """
        if stringToPrint is None:
            raise ValueError("stringToPrint cannot be None")

        text = str(stringToPrint)
        max_digits = config.SEVEN_SEGMENT_DIGITS

        tokens = []
        i = 0
        while i < len(text):
            if text[i] == "°":
                tokens.append("deg")
                i += 1
                continue

            if text[i:i + 3].lower() == "deg":
                tokens.append("deg")
                i += 3
                continue

            ch = text[i]
            if ch.isalpha():
                ch = ch.upper()
            tokens.append(ch)
            i += 1

        if len(tokens) > max_digits:
            raise ValueError(
                f"String too long for display: {len(tokens)} > {max_digits}"
            )

        supported = set("0123456789ABCDEF- ")
        for token in tokens:
            if token == "deg":
                continue
            if token not in supported:
                raise ValueError(f"Unsupported character for seven-segment display: {token!r}")

        start_digit = max_digits - len(tokens) if alighRight else 0

        # clear the digits 
        for digit in range(max_digits):
            self.__led.set_character(" ", digit=digit)

        for offset, token in enumerate(tokens):
            self.__led.set_character(token, digit=start_digit + offset)

        self.__led.draw()

    def clear(self) -> None:
        """Turn off all LEDs."""
        self.__led.clear().draw()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pass

    def show(self) -> None:
        """Update the display to show changes."""
        self.__led.draw()