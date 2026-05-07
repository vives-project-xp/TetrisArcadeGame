import math
from typing import List

import config
from cartridges.tetris_cartridge import COLORS, PIECES, PIECE_BLOCKS

OFF = (0, 0, 0)
MAIN_LANES = (
    {"center_x": 2, "start_delay_s": 0.0, "piece_offset": 0},
    {"center_x": 7, "start_delay_s": 0.45, "piece_offset": 3},
)
MAIN_SPAWN_SPACING_ROWS = 5
MAIN_FALL_SPEED = 5.2
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


def _falling_piece_state(
    current_time: float,
    lane_index: int,
    spawn_index: int,
) -> tuple[int, int, int, int, int]:
    lane = MAIN_LANES[lane_index]
    elapsed_for_lane = max(0.0, current_time - float(lane["start_delay_s"]))
    progress_rows = elapsed_for_lane * MAIN_FALL_SPEED
    top_left_y = math.floor(progress_rows - (spawn_index * MAIN_SPAWN_SPACING_ROWS)) - PIECE_BLOCKS

    piece_id = (spawn_index + int(lane["piece_offset"])) % len(PIECES)
    rotation = (spawn_index + lane_index) % 4
    color_index = (spawn_index + int(lane["piece_offset"]) + lane_index) % len(COLORS)

    piece = PIECES[piece_id][rotation]
    min_x, max_x, _, _ = _piece_bounds(piece)
    piece_center_x = (min_x + max_x) // 2
    top_left_x = int(lane["center_x"]) - piece_center_x

    return piece_id, rotation, color_index, top_left_x, top_left_y


def render_screensaver_main_display(current_time: float) -> List[List[tuple[int, int, int]]]:
    display = _empty_display(config.MAIN_MATRIX_WIDTH, config.MAIN_MATRIX_HEIGHT)
    visible_drop_count = (config.MAIN_MATRIX_HEIGHT // MAIN_SPAWN_SPACING_ROWS) + 3

    for lane_index in range(len(MAIN_LANES)):
        lane = MAIN_LANES[lane_index]
        elapsed_for_lane = max(0.0, current_time - float(lane["start_delay_s"]))
        latest_spawn_index = int((elapsed_for_lane * MAIN_FALL_SPEED) / MAIN_SPAWN_SPACING_ROWS)
        first_spawn_index = max(0, latest_spawn_index - visible_drop_count)

        for spawn_index in range(first_spawn_index, latest_spawn_index + 1):
            piece_id, rotation, color_index, top_left_x, top_left_y = _falling_piece_state(
                current_time,
                lane_index,
                spawn_index,
            )
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
