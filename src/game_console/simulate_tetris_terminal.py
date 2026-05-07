import sys
import time
import types
from typing import List, Set

try:
    import msvcrt
except ImportError as exc:
    raise RuntimeError("This terminal simulator currently requires Windows.") from exc

try:
    import board  # type: ignore
except ImportError:
    board = types.ModuleType("board")
    board.D10 = "D10"
    board.SCL = "SCL"
    board.SDA = "SDA"
    sys.modules["board"] = board

import config
from cartridges.tetris_cartridge import TetrisCartridge
from console.controls import ControlsEvent, ControlsState
from console.screensaver import (
    render_screensaver_main_display,
    render_screensaver_secondary_display,
    render_screensaver_segment_text,
)


KEY_EVENT_MAP = {
    " ": [ControlsEvent.BTN_START_PRESSED, ControlsEvent.BTN_START_RELEASED],
    "\r": [ControlsEvent.BTN_START_PRESSED, ControlsEvent.BTN_START_RELEASED],
    "w": [ControlsEvent.BTN_UP_PRESSED, ControlsEvent.BTN_UP_RELEASED],
    "W": [ControlsEvent.BTN_UP_PRESSED, ControlsEvent.BTN_UP_RELEASED],
    "a": [ControlsEvent.BTN_LEFT_PRESSED, ControlsEvent.BTN_LEFT_RELEASED],
    "A": [ControlsEvent.BTN_LEFT_PRESSED, ControlsEvent.BTN_LEFT_RELEASED],
    "s": [ControlsEvent.BTN_DOWN_PRESSED, ControlsEvent.BTN_DOWN_RELEASED],
    "S": [ControlsEvent.BTN_DOWN_PRESSED, ControlsEvent.BTN_DOWN_RELEASED],
    "d": [ControlsEvent.BTN_RIGHT_PRESSED, ControlsEvent.BTN_RIGHT_RELEASED],
    "D": [ControlsEvent.BTN_RIGHT_PRESSED, ControlsEvent.BTN_RIGHT_RELEASED],
}

ARROW_EVENT_MAP = {
    "H": [ControlsEvent.BTN_UP_PRESSED, ControlsEvent.BTN_UP_RELEASED],
    "K": [ControlsEvent.BTN_LEFT_PRESSED, ControlsEvent.BTN_LEFT_RELEASED],
    "P": [ControlsEvent.BTN_DOWN_PRESSED, ControlsEvent.BTN_DOWN_RELEASED],
    "M": [ControlsEvent.BTN_RIGHT_PRESSED, ControlsEvent.BTN_RIGHT_RELEASED],
}

COLOR_TO_CHAR = {
    (0xFF, 0x00, 0x00): "R",
    (0x00, 0xFF, 0x00): "G",
    (0x00, 0x00, 0xFF): "B",
    (0x00, 0xFF, 0xFF): "C",
    (0xFF, 0x00, 0xFF): "M",
    (0xFF, 0xFF, 0x00): "Y",
    (0xFF, 0xFF, 0xFF): "W",
}


class FakeSound:
    def __init__(self, title: str, console: "FakeConsole") -> None:
        self.title = title
        self.console = console
        self.play_count = 0

    def play(self) -> None:
        self.play_count += 1
        self.console.last_sound_played = self.title


class FakeConsole:
    def __init__(self) -> None:
        self.cartridge = None
        self.main_display = self._blank_display(
            config.MAIN_MATRIX_HEIGHT,
            config.MAIN_MATRIX_WIDTH,
        )
        self.secondary_display = self._blank_display(
            config.SECONDARY_MATRIX_HEIGHT,
            config.SECONDARY_MATRIX_WIDTH,
        )
        self.segment_text = "----"
        self.music_title = None
        self.music_paused = False
        self.last_sound_played = None
        self.active_states: Set[ControlsState] = set()
        self.last_input_time = time.perf_counter()
        self.screensaver_active = False

    def _blank_display(self, height: int, width: int) -> List[List[tuple[int, int, int]]]:
        return [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def insert_cartridge(self, cartridge) -> None:
        self.cartridge = cartridge
        self.screensaver_active = False
        self.last_input_time = time.perf_counter()
        cartridge.init(self)

    def clear_all(self) -> None:
        self.fill_main_display((0, 0, 0))
        self.fill_secondary_display((0, 0, 0))
        self.set_segment_display_text("    ")

    def draw_main_display(self, rgbll: List[List[tuple[int, int, int]]]) -> None:
        self.main_display = [row[:] for row in rgbll]

    def draw_secondary_display(self, rgbll: List[List[tuple[int, int, int]]]) -> None:
        self.secondary_display = [row[:] for row in rgbll]

    def fill_main_display(self, rgb: tuple[int, int, int]) -> None:
        self.main_display = [
            [rgb for _ in range(config.MAIN_MATRIX_WIDTH)]
            for _ in range(config.MAIN_MATRIX_HEIGHT)
        ]

    def fill_secondary_display(self, rgb: tuple[int, int, int]) -> None:
        self.secondary_display = [
            [rgb for _ in range(config.SECONDARY_MATRIX_WIDTH)]
            for _ in range(config.SECONDARY_MATRIX_HEIGHT)
        ]

    def set_segment_display_text(self, text: str, alighRight: bool = False) -> None:
        rendered = str(text)
        if alighRight:
            rendered = rendered.rjust(config.SEVEN_SEGMENT_DIGITS)
        self.segment_text = rendered[:config.SEVEN_SEGMENT_DIGITS]

    def commit_displays(self) -> None:
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.write(f"Mode: {'screensaver' if self.screensaver_active else 'cartridge'}\n")
        sys.stdout.write(f"Score: {self.segment_text}\n")
        sys.stdout.write(
            f"Music: {self.music_title or '-'}"
            f"{' (paused)' if self.music_paused else ''}\n"
        )
        if self.last_sound_played:
            sys.stdout.write(f"Last sound: {self.last_sound_played}\n")
        else:
            sys.stdout.write("Last sound: -\n")
        sys.stdout.write("Controls: A/D left-right, S down, W rotate, SPACE start, T screensaver, Q quit\n")
        sys.stdout.write("\n")

        main_lines = self._display_to_lines(self.main_display)
        next_lines = self._display_to_lines(self.secondary_display)

        sys.stdout.write("Board          Next\n")
        sys.stdout.write(f"+{'-' * config.MAIN_MATRIX_WIDTH}+    +{'-' * config.SECONDARY_MATRIX_WIDTH}+\n")
        for row_index in range(config.MAIN_MATRIX_HEIGHT):
            next_part = next_lines[row_index] if row_index < len(next_lines) else " " * config.SECONDARY_MATRIX_WIDTH
            sys.stdout.write(f"|{main_lines[row_index]}|    |{next_part}|\n")
        sys.stdout.write(f"+{'-' * config.MAIN_MATRIX_WIDTH}+    +{'-' * config.SECONDARY_MATRIX_WIDTH}+\n")
        sys.stdout.flush()

    def _display_to_lines(self, rgbll: List[List[tuple[int, int, int]]]) -> List[str]:
        lines = []
        for row in rgbll:
            chars = []
            for rgb in row:
                chars.append(self._rgb_to_char(rgb))
            lines.append("".join(chars))
        return lines

    "for terminal display"
    def _rgb_to_char(self, rgb: tuple[int, int, int]) -> str:
        if rgb == (0, 0, 0):
            return "."

        red, green, blue = rgb
        brightest = max(rgb)
        darkest = min(rgb)

        if brightest < 35:
            return "."
        if brightest - darkest < 35:
            return "W" if brightest > 160 else "+"
        if abs(red - green) < 40 and red > blue:
            return "Y"
        if abs(red - blue) < 40 and red > green:
            return "M"
        if abs(green - blue) < 40 and green > red:
            return "C"
        if brightest == red:
            return "R"
        if brightest == green:
            return "G"
        return "B"

    def get_active_control_states(self) -> Set[ControlsState]:
        return set(self.active_states)

    def load_sound(self, sound_title: str) -> FakeSound:
        return FakeSound(sound_title, self)

    def load_music(self, music_title: str) -> None:
        self.music_title = music_title

    def replay_music(self) -> None:
        self.music_paused = False

    def pause_music(self) -> None:
        self.music_paused = True

    def set_music_volume(self, volume: float) -> None:
        return None

    def run(self) -> None:
        if not self.cartridge:
            return

        try:
            while True:
                current_time = time.perf_counter()
                controls_update, should_quit, force_screensaver = poll_terminal_events()
                if should_quit:
                    break

                if force_screensaver and self.cartridge and self.cartridge.can_enter_screensaver():
                    self.screensaver_active = True
                    self._draw_screensaver_frame(current_time)
                    self.commit_displays()
                    time.sleep(config.FRAME_TIME)
                    continue

                if controls_update:
                    self.last_input_time = current_time
                    if self.screensaver_active:
                        self._deactivate_screensaver()
                        time.sleep(config.FRAME_TIME)
                        continue

                if self.screensaver_active:
                    self._draw_screensaver_frame(current_time)
                    self.commit_displays()
                    time.sleep(config.FRAME_TIME)
                    continue

                if self._should_activate_screensaver(current_time):
                    self.screensaver_active = True
                    self._draw_screensaver_frame(current_time)
                    self.commit_displays()
                    time.sleep(config.FRAME_TIME)
                    continue

                if ControlsEvent.BTN_START_RELEASED in controls_update:
                    self.cartridge.start_new_game()

                self.cartridge.tick(current_time, controls_update)
                time.sleep(config.FRAME_TIME)
        except KeyboardInterrupt:
            pass

    def _should_activate_screensaver(self, current_time: float) -> bool:
        if not self.cartridge or not self.cartridge.can_enter_screensaver():
            return False
        return (current_time - self.last_input_time) >= config.SCREENSAVER_TIMEOUT_S

    def _deactivate_screensaver(self) -> None:
        self.screensaver_active = False
        self.clear_all()
        if self.cartridge:
            self.cartridge.force_update()

    def _draw_screensaver_frame(self, current_time: float) -> None:
        self.draw_main_display(render_screensaver_main_display(current_time))
        self.draw_secondary_display(render_screensaver_secondary_display(current_time))
        self.set_segment_display_text(render_screensaver_segment_text(current_time))

def poll_terminal_events() -> tuple[List[ControlsEvent], bool, bool]:
    events: List[ControlsEvent] = []
    should_quit = False
    force_screensaver = False

    while msvcrt.kbhit():
        key = msvcrt.getwch()

        if key in ("\x00", "\xe0"):
            arrow_key = msvcrt.getwch()
            events.extend(ARROW_EVENT_MAP.get(arrow_key, []))
            continue

        if key in ("q", "Q"):
            should_quit = True
            continue

        if key in ("t", "T"):
            force_screensaver = True
            continue

        events.extend(KEY_EVENT_MAP.get(key, []))

    return events, should_quit, force_screensaver


def main() -> None:
    console = FakeConsole()
    console.insert_cartridge(TetrisCartridge())
    console.run()


if __name__ == "__main__":
    main()
