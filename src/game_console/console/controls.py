from enum import Enum, auto


class ControlsState(Enum):
    """The state of controls (held buttons)."""
    BTN_START_HOLD = auto()
    BTN_UP_HOLD = auto()
    BTN_RIGHT_HOLD = auto()
    BTN_DOWN_HOLD = auto()
    BTN_LEFT_HOLD = auto()


class ControlsEvent(Enum):
    """Control events (button press/release)."""
    BTN_START_PRESSED = auto()
    BTN_START_RELEASED = auto()
    BTN_UP_PRESSED = auto()
    BTN_UP_RELEASED = auto()
    BTN_RIGHT_PRESSED = auto()
    BTN_RIGHT_RELEASED = auto()
    BTN_DOWN_PRESSED = auto()
    BTN_DOWN_RELEASED = auto()
    BTN_LEFT_PRESSED = auto()
    BTN_LEFT_RELEASED = auto()

def control_state_to_event(state: ControlsState, pressed: bool) -> ControlsEvent:
    """
    Converts a control state to a control event.
    
    Args:
        state: The control state
        pressed: True for pressed event, False for released event
        
    Returns:
        The corresponding ControlsEvent
    """
    suffix = "PRESSED" if pressed else "RELEASED"
    event_name = state.name.replace("_HOLD", f"_{suffix}")
    return ControlsEvent[event_name]