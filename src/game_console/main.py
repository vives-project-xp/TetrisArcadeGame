from cartridges.test_cartridge import TestCartridge
from cartridges.tetris_cartridge import TetrisCartridge
from console.game_console import GameConsole


def main() -> None:
    """Main entry point for the game console."""
    console = GameConsole()
    console.insert_cartridge(TetrisCartridge())
    console.run()


if __name__ == "__main__":
    main()