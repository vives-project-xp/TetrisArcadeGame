import time
import config
from typing import List, Optional, Set
from console.controls import ControlsState, ControlsEvent
from cartridges.base_cartridge import GameCartridge
from console.input_manager import InputManager
from console.led_strip import LEDStrip
from console.seven_segment import SevenSegment
from console.screensaver import (
    render_screensaver_main_display,
    render_screensaver_secondary_display,
    render_screensaver_segment_text,
)
import pygame


class GameConsole:
    """
    Main game console class that manages display, input, audio, and cartridges.
    
    """

    def __init__(self):
        """Initializes the game console."""
        self.__input_manager = InputManager()
        self.__led_strip = LEDStrip(config.LED_STRIP_LEN, config.LED_STRIP_PIN)
        self.__seven_segment = SevenSegment()
        self.__game_cartridge = None
        self.__last_input_time = time.perf_counter()
        self.__screensaver_active = False
        self.__screensaver_started_at = 0.0
        self.__game_cartridge_index = 0
        self.__available_cartridges = []
        pygame.mixer.init(channels=1)
        
    def set_available_cartridges(self, cartridges: List[type]) -> None:
        self.__available_cartridges = cartridges

    def run(self):
        """Starts the game console and game loop."""
        if not self.__game_cartridge:
            return None
        try:
            start_btn_press_time = 0.0
            
            while True:
                current_time = time.perf_counter()
                controls_update = self.__input_manager.poll_inputs()
                if controls_update:
                    self.__last_input_time = current_time
                    if self.__screensaver_active:
                        self.__deactivate_screensaver()
                        time.sleep(config.FRAME_TIME)
                        continue

                if self.__screensaver_active:
                    self.__draw_screensaver_frame(current_time)
                    self.commit_displays()
                    time.sleep(config.FRAME_TIME)
                    continue

                if self.__should_activate_screensaver(current_time):
                    self.__screensaver_active = True
                    self.__screensaver_started_at = current_time
                    self.__draw_screensaver_frame(current_time)
                    self.commit_displays()
                    time.sleep(config.FRAME_TIME)
                    continue

                if ControlsEvent.BTN_START_PRESSED in controls_update:
                    start_btn_press_time = current_time

                if ControlsEvent.BTN_START_RELEASED in controls_update:
                    if start_btn_press_time > 0 and current_time - start_btn_press_time >= 1.5:
                        if self.__available_cartridges:
                            self.__game_cartridge_index = (self.__game_cartridge_index + 1) % len(self.__available_cartridges)
                            self.insert_cartridge(self.__available_cartridges[self.__game_cartridge_index]())
                            start_btn_press_time = 0.0
                            continue
                    else:
                        self.__game_cartridge.start_new_game()
                    start_btn_press_time = 0.0
                    
                self.__game_cartridge.tick(current_time, controls_update)
                time.sleep(config.FRAME_TIME)
        except KeyboardInterrupt:
            self.insert_cartridge(None)
            self.__input_manager.cleanup()
            pygame.mixer.stop()

    def clear_all(self) -> None:
        """Clear all displays."""
        self.__led_strip.clear()
        self.__seven_segment.clear()

    def __rgb_matrix_to_linear(self, rgbll: List[List[tuple]], inverted: bool = False) -> List[tuple]:
        if not rgbll:
            return []
        width = len(rgbll[0])
        result = []
        # transform from top-left to bottom-left coordinates
        if not inverted: 
            rgbll.reverse()
        for i, row_rgbl in enumerate(rgbll):
            if width != len(row_rgbl):
                raise ValueError("Inconsistent width of the arrays")
            # transform to zigzag
            if i % 2 == 0 and not inverted:
                row_rgbl.reverse()
            if i % 2 == 1 and inverted:
                row_rgbl.reverse()
            result.extend(row_rgbl)
        return result
    
    def __draw_strip(self, rgbl: List[tuple], offset: int = 0) -> None:
        for i, rgb in enumerate(rgbl, start=offset):
            self.__led_strip.set_pixel(i, rgb)
    
    def commit_displays(self) -> None:
        self.__led_strip.show()
        self.__seven_segment.show()
    
    def draw_main_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to the main LED matrix display.
        
        Args:
            rgbll: 2D list of RGB tuples representing the 10x20 matrix
        """
        self.__draw_strip(self.__rgb_matrix_to_linear(rgbll), config.MAIN_MATRIX_OFFSET)
    
    def draw_secondary_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to a secondary display.
        
        Args:
            rgbll: 2D list of RGB tuples
        """
        self.__draw_strip(self.__rgb_matrix_to_linear(rgbll, inverted = True), config.SECONDARY_MATRIX_OFFSET)
    
    def fill_main_display(self, rgb) -> None:
        self.__led_strip.fill(config.MAIN_MATRIX_OFFSET, config.MAIN_MATRIX_PIX_COUNT, rgb)
    
    def fill_secondary_display(self, rgb) -> None:
        self.__led_strip.fill(config.SECONDARY_MATRIX_OFFSET, config.SECONDARY_MATRIX_PIX_COUNT, rgb)
    
    def set_segment_display_text(self, text: str, alighRight : bool = False) -> None:
        """
        Set text on a seven segment display.
        
        Supported symbols: 0-9, A-F, '-', ' ', and degree ('deg' or '°').
        
        Args:
            text: Text to display, max 4 chars
        """
        self.__seven_segment.print_string(text, alighRight)

    def set_segment_display_colon(self, pattern) -> None:
        """Set which colon/point indicators are illuminated on the seven-segment display.

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
        self.__seven_segment.set_colon(pattern)
    
    def insert_cartridge(self, cartridge: GameCartridge | None) -> None:
        """
        Insert a game cartridge into the console.
        
        Args:
            cartridge: GameCartridge instance to insert
        """
        if self.__game_cartridge:
            self.__game_cartridge.deinit()
        self.__game_cartridge = None
        self.__screensaver_active = False
        self.__screensaver_started_at = 0.0
        self.__last_input_time = time.perf_counter()
        self.clear_all()
        if cartridge:
            self.__game_cartridge = cartridge
            cartridge.init(self)
    
    def get_active_control_states(self) -> Set[ControlsState]:
        """
        Gets the currently acive controls.
        
        Returns:
            Set of currently active ControlsState
        """
        return self.__input_manager.get_current_states()
    
    def load_sound(self, sound_title: str) -> None:
        """
        Load a sound effect.
        
        Args:
            sound_title: Title of the sound to load
        """
        sound = pygame.mixer.Sound("assets/sounds/" + sound_title)
        return sound
        
    def load_music(self, music_title: str) -> None:
        """
        Load background music.
        
        Args:
            music_title: Title of the music file to load
        """
        pygame.mixer.music.load("assets/music/" + music_title)
    
    def unload_music(self) -> None:
        """Unload the current music."""
        pygame.mixer.music.unload()

    def replay_music(self) -> None:
        """Replay the current music."""
        pygame.mixer.music.play(-1)

    def pause_music(self) -> None:
        """Pause the current music."""
        pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        """Resume the paused music."""
        pygame.mixer.music.unpause()

    def play_music(self) -> None:
        """Play the loaded music."""
        pygame.mixer.music.play(-1)
        
    def fadeout_music(self, fade_time: int) -> None:
        """Fade out the music."""
        pygame.mixer.music.fadeout(fade_time)
    
    def set_music_volume(self, volume: float) -> None:
        """
        Set the music volume.
        
        Args:
            volume: Volume level from 0.0 to 1.0
        """
        pygame.mixer.music.set_volume(volume)
    
    def pause(self) -> None:
        """Pause the game console."""
        pass

    def __should_activate_screensaver(self, current_time: float) -> bool:
        if not self.__game_cartridge or not self.__game_cartridge.can_enter_screensaver():
            return False
        return (current_time - self.__last_input_time) >= config.SCREENSAVER_TIMEOUT_S

    def __deactivate_screensaver(self) -> None:
        self.__screensaver_active = False
        self.__screensaver_started_at = 0.0
        self.clear_all()
        if self.__game_cartridge:
            self.__game_cartridge.force_update()

    def __draw_screensaver_frame(self, current_time: float) -> None:
        elapsed = max(0.0, current_time - self.__screensaver_started_at)
        self.draw_main_display(render_screensaver_main_display(elapsed))
        self.draw_secondary_display(render_screensaver_secondary_display(elapsed))
        self.set_segment_display_text(render_screensaver_segment_text(elapsed))
