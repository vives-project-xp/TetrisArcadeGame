from typing import List, Set, Dict
import threading

from RPi import GPIO
import config
from console.controls import ControlsState, ControlsEvent, control_state_to_event

BOUNCE_TIME_MS = 50


class InputManager:
    """
    Manages input from physical buttons.
    Translates inputs to ControlsEvent and ControlsState.
    """
    
    def __init__(self) -> None:
        self.__btn_updates = []
        self.__btn_updates_lock = threading.Lock()
        self.init_physical_buttons(config.BUTTON_GPIO_MAPPING)
        pass
    
    def init_physical_buttons(self, gpio_pin_mapping: Dict[int, ControlsState]) -> None:
        """
        Initialize GPIO pins for physical buttons.
        
        Args:
            gpio_pin_mapping: Mapping of GPIO pins to ControlsState
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)
        for pin_id in gpio_pin_mapping:
            GPIO.setup(pin_id, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin_id, GPIO.BOTH, callback=self._btn_callback, bouncetime=BOUNCE_TIME_MS)

    def _btn_callback(self, channel) -> None:
        pressed = GPIO.input(channel) == GPIO.LOW
        event = self.translate_button_to_event(channel, pressed)
        with self.__btn_updates_lock:
            self.__btn_updates.append(event)

    def poll_inputs(self) -> List[ControlsEvent]:
        """
        Poll all input sources and return control events.
        
        Returns:
            List of ControlsEvent that occurred since last poll
        """
        with self.__btn_updates_lock:
            result = self.__btn_updates.copy()
            self.__btn_updates.clear()
        return result
    
    def get_current_states(self) -> Set[ControlsState]:
        """
        Get the current state of all controls.
        
        Returns:
            Set of currently active ControlsState
        """
        active_states = set()
        for pin_id, control_state in config.BUTTON_GPIO_MAPPING.items():
            if GPIO.input(pin_id) == GPIO.LOW:
                active_states.add(control_state)
        return active_states
    
    def translate_button_to_event(self, gpio_pin: int, pressed: bool) -> ControlsEvent:
        return control_state_to_event(config.BUTTON_GPIO_MAPPING.get(gpio_pin), pressed)
    
    def cleanup(self) -> None:
        GPIO.cleanup()
        pass