import time
import config
from typing import List, Optional, Set
from console.controls import ControlsState, ControlsEvent
from cartridges.base_cartridge import GameCartridge
from console.input_manager import InputManager


class GameConsole:
    """
    Main game console class that manages display, input, audio, and cartridges.
    
    """

    def __init__(self):
        """Initializes the game console."""
        self.__input_manager = InputManager()
    
    def run(self):
        """Starts the game console and game loop."""
        try:
            while True:
                controls_update = self.__input_manager.poll_inputs()
                if controls_update:
                    print(controls_update)
                time.sleep(config.FRAME_TIME)
        except KeyboardInterrupt:
            self.__input_manager.cleanup()

    def clear_all(self) -> None:
        """Clear all displays."""
        pass
    
    def draw_main_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to the main LED matrix display.
        
        Args:
            rgbll: 2D list of RGB tuples representing the 10x20 matrix
        """
        pass
    
    def draw_secondary_display(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to a secondary display.
        
        Args:
            rgbll: 2D list of RGB tuples
        """
        pass
    
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
        pass
    
    def get_active_control_states(self) -> Set[ControlsState]:
        """
        Gets the currently acive controls.
        
        Returns:
            Set of currently active ControlsState
        """
        return self.__input_manager.get_current_states()
    
    def play_sound(self, sound_title: str) -> None:
        """
        Play a sound effect.
        
        Args:
            sound_title: Title of the sound to play
        """
        pass
    
    def pause(self) -> None:
        """Pause the game console."""
        pass