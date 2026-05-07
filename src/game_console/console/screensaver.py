import math
from typing import List

import config
from cartridges.tetris_cartridge import COLORS, PIECES, PIECE_BLOCKS

OFF = (0, 0, 0)
MAIN_STREAMS = (
    {"lane_x": 1, "speed": 4.2, "time_offset": 0.0, "piece_offset": 0},
    {"lane_x": 4, "speed": 3.6, "time_offset": 1.7, "piece_offset": 2},
    {"lane_x": 7, "speed": 4.8, "time_offset": 3.1, "piece_offset": 4},
)
PREVIEW_CHANGE_INTERVAL_S = 2.0


def _empty_display(width: int, height: int) -> List[List[tuple[int, int, int]]]:
    return [[OFF for _ in range(width)] for _ in range(height)]


def _piece_bounds(piece: List[List[int]]) -> tuple[int, int, int, int]:
    min_x = PIECE_BLOCKS
    max_x = 0
    min_y = PIECE_BLOCKS
    max_y = 0

    for y in range(PIECE_BLOCKS):
        for x in range(PIECE_BLOCKS):
            if piece[y][x] == 0:
                continue
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

    return min_x, max_x, min_y, max_y


def _draw_piece(
    display: List[List[tuple[int, int, int]]],
    piece_id: int,
    rotation: int,
    top_left_x: int,
    top_left_y: int,
    color: tuple[int, int, int],
) -> None:
    piece = PIECES[piece_id][rotation]
    display_height = len(display)
    display_width = len(display[0]) if display else 0

    for y in range(PIECE_BLOCKS):
        for x in range(PIECE_BLOCKS):
            if piece[y][x] == 0:
                continue
            draw_x = top_left_x + x
            draw_y = top_left_y + y
            if 0 <= draw_x < display_width and 0 <= draw_y < display_height:
                display[draw_y][draw_x] = color


def _stream_piece_state(current_time: float, stream_index: int) -> tuple[int, int, int, int, int]:
    stream = MAIN_STREAMS[stream_index]
    travel_rows = config.MAIN_MATRIX_HEIGHT + PIECE_BLOCKS + 2
    cycle_duration = travel_rows / stream["speed"]
    stream_time = current_time + stream["time_offset"]
    cycle_index = int(stream_time / cycle_duration)
    cycle_progress = stream_time % cycle_duration

    piece_id = (cycle_index + stream["piece_offset"]) % len(PIECES)
    rotation = (cycle_index + stream_index) % 4
    color_index = (cycle_index + stream["piece_offset"]) % len(COLORS)
    top_left_y = math.floor(cycle_progress * stream["speed"]) - PIECE_BLOCKS

    piece = PIECES[piece_id][rotation]
    min_x, max_x, _, _ = _piece_bounds(piece)
    piece_center_x = (min_x + max_x) // 2
    top_left_x = stream["lane_x"] - piece_center_x

    return piece_id, rotation, color_index, top_left_x, top_left_y


def render_screensaver_main_display(current_time: float) -> List[List[tuple[int, int, int]]]:
    display = _empty_display(config.MAIN_MATRIX_WIDTH, config.MAIN_MATRIX_HEIGHT)

    for stream_index in range(len(MAIN_STREAMS)):
        piece_id, rotation, color_index, top_left_x, top_left_y = _stream_piece_state(current_time, stream_index)
        _draw_piece(display, piece_id, rotation, top_left_x, top_left_y, COLORS[color_index])

    return display


def render_screensaver_secondary_display(current_time: float) -> List[List[tuple[int, int, int]]]:
    display = _empty_display(config.SECONDARY_MATRIX_WIDTH, config.SECONDARY_MATRIX_HEIGHT)
    preview_index = int(current_time / PREVIEW_CHANGE_INTERVAL_S)
    piece_id = preview_index % len(PIECES)
    rotation = preview_index % 4
    color = COLORS[preview_index % len(COLORS)]

    _draw_piece(display, piece_id, rotation, 0, 0, color)
    return display


def render_screensaver_segment_text(current_time: float) -> str:
    return "----"
