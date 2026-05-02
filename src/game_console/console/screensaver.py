import colorsys
import math
from typing import List

import config


def _hsv_to_rgb_tuple(hue: float, saturation: float, value: float) -> tuple[int, int, int]:
    red, green, blue = colorsys.hsv_to_rgb(hue % 1.0, max(0.0, min(1.0, saturation)), max(0.0, min(1.0, value)))
    return (
        int(red * 255),
        int(green * 255),
        int(blue * 255),
    )


def render_screensaver_main_display(current_time: float) -> List[List[tuple[int, int, int]]]:
    display = []
    for y in range(config.MAIN_MATRIX_HEIGHT):
        row = []
        for x in range(config.MAIN_MATRIX_WIDTH):
            hue = current_time * 0.07 + (x / config.MAIN_MATRIX_WIDTH) * 0.22 + (y / config.MAIN_MATRIX_HEIGHT) * 0.08
            wave = 0.5 + 0.5 * math.sin((x * 0.85) + (y * 0.45) - (current_time * 3.0))
            sparkle = 0.35 + 0.65 * math.sin(current_time * 1.2 + y * 0.18) ** 2
            row.append(_hsv_to_rgb_tuple(hue, 1.0, 0.12 + (wave * sparkle * 0.88)))
        display.append(row)
    return display


def render_screensaver_secondary_display(current_time: float) -> List[List[tuple[int, int, int]]]:
    display = []
    center_x = (config.SECONDARY_MATRIX_WIDTH - 1) / 2
    center_y = (config.SECONDARY_MATRIX_HEIGHT - 1) / 2
    pulse = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(current_time * 3.5))

    for y in range(config.SECONDARY_MATRIX_HEIGHT):
        row = []
        for x in range(config.SECONDARY_MATRIX_WIDTH):
            distance = abs(x - center_x) + abs(y - center_y)
            ring = max(0.0, 1.0 - (distance / 3.0))
            hue = current_time * 0.15 + distance * 0.08
            row.append(_hsv_to_rgb_tuple(hue, 1.0, ring * pulse))
        display.append(row)
    return display


def render_screensaver_segment_text(current_time: float) -> str:
    return "----" if int(current_time / 0.5) % 2 == 0 else "    "
