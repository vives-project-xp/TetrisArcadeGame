from typing import List, Set, Dict, Callable

from RPi import GPIO
import config
from console.controls import ControlsState, ControlsEvent, control_state_to_event
import time


class InputManager:
    """
    Manages input from physical buttons and keyboard.
    Translates inputs to ControlsEvent and ControlsState.
    """
    
    def __init__(self) -> None:
        self.init_physical_buttons(config.BUTTON_GPIO_MAPPING)
        self.init_keyboard_mapping()
        pass
    
    def init_physical_buttons(self, gpio_pin_mapping: Dict[int, ControlsState]) -> None:
        """
        Initialize GPIO pins for physical buttons.
        
        Args:
            gpio_pin_mapping: Mapping of GPIO pins to ControlsState
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)
        for pin_id, controls_state in gpio_pin_mapping:
            GPIO.setup(pin_id, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin_id, GPIO.FALLING)
    
    def init_keyboard_mapping(self, key_mapping: Dict[str, ControlsState]) -> None:
        """
        Initialize keyboard to controls mapping.
        
        Args:
            key_mapping: Mapping of keyboard keys to ControlsState
                        e.g., {'w': ControlsState.BTN_UP_HOLD, ...}
        """
        pass
    
    def start_keyboard_listener(self) -> None:
        """Start listening for keyboard events."""
        pass
    
    def stop_keyboard_listener(self) -> None:
        """Stop listening for keyboard events."""
        pass

    def poll_inputs(self) -> List[ControlsEvent]:
        """
        Poll all input sources and return control events.
        
        Returns:
            List of ControlsEvent that occurred since last poll
        """
        result = []
        for pin_id, controls_state in config.BUTTON_GPIO_MAPPING:
            if GPIO.event_detected(pin_id):
                result.append(control_state_to_event(controls_state, True))
                #TODO continue here, also detect releases
        
        return result
    
    def get_current_states(self) -> Set[ControlsState]:
        """
        Get the current state of all controls.
        
        Returns:
            Set of currently active ControlsState
        """
        pass
    
    def translate_keyboard_to_event(self, key: str, pressed: bool) -> ControlsEvent:
        """
        Translate keyboard input to control event.
        
        Args:
            key: The keyboard key
            pressed: True if pressed, False if released
            
        Returns:
            Corresponding ControlsEvent
        """
        pass
    
    def translate_button_to_event(self, gpio_pin: int, pressed: bool) -> ControlsEvent:
        return control_state_to_event(config.BUTTON_GPIO_MAPPING.get(gpio_pin), pressed)
    
    def cleanup(self) -> None:
        """Clean up GPIO and keyboard listeners."""
        GPIO.cleanup()
        pass