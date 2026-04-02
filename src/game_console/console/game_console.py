import time
import config
from typing import List, Optional, Set
from console.controls import ControlsState, ControlsEvent
from cartridges.base_cartridge import GameCartridge
from console.input_manager import InputManager
from console.led_strip import LEDStrip
import pygame


class GameConsole:
    """
    Main game console class that manages display, input, audio, and cartridges.
    
    """

    def __init__(self):
        """Initializes the game console."""
        self.__input_manager = InputManager()
        self.__led_strip = LEDStrip(config.LED_STRIP_LEN, config.LED_STRIP_PIN)
        self.__game_cartridge = None
        pygame.mixer.init(channels=1)
    
    def run(self):
        """Starts the game console and game loop."""
        if not self.__game_cartridge:
            return None
        try:
            while True:
                controls_update = self.__input_manager.poll_inputs()
                self.__game_cartridge.tick(time.perf_counter(), controls_update)
                time.sleep(config.FRAME_TIME)
        except KeyboardInterrupt:
            self.insert_cartridge(None)
            self.__input_manager.cleanup()
            pygame.mixer.stop()

    def clear_all(self) -> None:
        """Clear all displays."""
        self.__led_strip.clear()
        pass

    def __rgb_matrix_to_linear(self, rgbll: List[List[tuple]]) -> List[tuple]:
        if not rgbll:
            return []
        width = len(rgbll[0])
        result = []
        # transform from top-left to bottom-left coordinates
        rgbll.reverse()
        for i, row_rgbl in enumerate(rgbll):
            if width != len(row_rgbl):
                raise ValueError("Inconsistent width of the arrays")
            if i % 2 == 0:
                # transform to zigzag
                row_rgbl.reverse()
            result.extend(row_rgbl)
        return result
    
    def __draw_strip(self, rgbl: List[tuple], offset: int = 0) -> None:
        for i, rgb in enumerate(rgbl, start=offset):
            self.__led_strip.set_pixel(i, rgb)
    
    def commit_displays(self) -> None:
        self.__led_strip.show()
    
    def draw_main_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to the main LED matrix display.
        
        Args:
            rgbll: 2D list of RGB tuples representing the 10x20 matrix
        """
        print("will draw this:")
        for row in rgbll:
            print(''.join('.' if rgb == (0, 0, 0) else 'X' for rgb in row))
        print()
        self.__draw_strip(self.__rgb_matrix_to_linear(rgbll), config.MAIN_MATRIX_OFFSET)
        print("did draw this:")
        for row in rgbll:
            print(''.join('.' if rgb == (0, 0, 0) else 'X' for rgb in row))
        print()
    
    def draw_secondary_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to a secondary display.
        
        Args:
            rgbll: 2D list of RGB tuples
        """
        self.__draw_strip(self.__rgb_matrix_to_linear(rgbll), config.SECONDARY_MATRIX_OFFSET)
    
    def fill_main_display(self, rgb) -> None:
        self.__led_strip.fill(config.MAIN_MATRIX_OFFSET, config.MAIN_MATRIX_PIX_COUNT, rgb)
    
    def fill_secondary_display(self, rgb) -> None:
        self.__led_strip.fill(config.SECONDARY_MATRIX_OFFSET, config.SECONDARY_MATRIX_PIX_COUNT, rgb)
    
    def set_segment_display_text(self, text: str) -> None:
        """
        Set text on a seven segment display.
        
        Args:
            text: Text to display
        """
        pass
    
    def insert_cartridge(self, cartridge: GameCartridge) -> None:
        """
        Insert a game cartridge into the console.
        
        Args:
            cartridge: GameCartridge instance to insert
        """
        if self.__game_cartridge:
            self.__game_cartridge.deinit()
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