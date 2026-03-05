from typing import List, Optional, Set
from console.controls import ControlsState, ControlsEvent
from cartridges.base_cartridge import GameCartridge


class GameConsole:
    """
    Main game console class that manages display, input, audio, and cartridges.
    
    """
    
    def clearAll(self) -> None:
        """Clear all displays."""
        pass
    
    def drawMainDisplay(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to the main LED matrix display.
        
        Args:
            rgbll: 2D list of RGB tuples representing the 10x20 matrix
        """
        pass
    
    def drawSecondaryDisplay(self, rgbll: List[List[tuple]]) -> None:
        """
        Draw to a secondary display.
        
        Args:
            rgbll: 2D list of RGB tuples
        """
        pass
    
    def setSegmentDisplayText(self, text: str) -> None:
        """
        Set text on a seven segment display.
        
        Args:
            text: Text to display
        """
        pass
    
    def insertCartridge(self, cartridge: GameCartridge) -> None:
        """
        Insert a game cartridge into the console.
        
        Args:
            cartridge: GameCartridge instance to insert
        """
        pass
    
    def isControlState(self, controls_state: ControlsState) -> bool:
        """
        Check if a control is in a specific state.
        
        Args:
            controls_state: The control state to check
            
        Returns:
            True if the control is in the specified state, False otherwise
        """
        pass
    
    def playSound(self, sound_title: str) -> None:
        """
        Play a sound effect.
        
        Args:
            sound_title: Title of the sound to play
        """
        pass
    
    def pause(self) -> None:
        """Pause the game console."""
        pass