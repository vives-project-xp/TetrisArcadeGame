from console.controls import ControlsState

# Game loop settings
TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS

# Display settings
MATRIX_WIDTH = 10
MATRIX_HEIGHT = 20
LED_STRIP_PIN = 15
LED_BRIGHTNESS = 1.0

# GPIO pin mappings for physical buttons (BCM)
BUTTON_GPIO_MAPPING = {
    # 17: ControlsState.BTN_UP_HOLD,
    # 27: ControlsState.BTN_DOWN_HOLD,
    26: ControlsState.BTN_LEFT_HOLD,
    20: ControlsState.BTN_RIGHT_HOLD,
}

# Audio settings
AUDIO_ASSETS_PATH = "assets/sounds/"
AUDIO_SAMPLE_RATE = 22050
AUDIO_BUFFER_SIZE = 512