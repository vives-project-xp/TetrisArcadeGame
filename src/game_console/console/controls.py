from enum import Enum, auto


class ControlsState(Enum):
    """The state of controls (held buttons)."""
    BTN_START_HOLD = auto()
    BTN_DOWN_HOLD = auto()
    BTN_RIGHT_HOLD = auto()
    BTN_LEFT_HOLD = auto()
    BTN_UP_HOLD = auto()
    BTN_DOWN_HOLD = auto()


class ControlsEvent(Enum):
    """Control events (button press/release)."""
    BTN_START_PRESSED = auto()
    BTN_START_RELEASED = auto()
    BTN_DOWN_PRESSED = auto()
    BTN_DOWN_RELEASED = auto()
    BTN_RIGHT_PRESSED = auto()
    BTN_RIGHT_RELEASED = auto()
    BTN_LEFT_PRESSED = auto()
    BTN_LEFT_RELEASED = auto()
    BTN_UP_PRESSED = auto()
    BTN_UP_RELEASED = auto()
    BTN_DOWN_PRESSED = auto()
    BTN_DOWN_RELEASED = auto()