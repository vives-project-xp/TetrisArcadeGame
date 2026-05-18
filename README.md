# TETRIS ARCADE GAME

[![VIVES Elektronica-ICT](https://img.shields.io/badge/VIVES-Bachelor_Electronica--ICT-blue?style=flat)](https://www.vives.be/nl/technology/elektronica-ict)
[![Project Experience](https://img.shields.io/badge/VIVES-Project_Experience-green?style=flat)](https://github.com/vives-project-xp)
[![GitHub](https://img.shields.io/github/stars/vives-project-xp/TetrisArcadeGame?style=social)](https://github.com/vives-project-xp/TetrisArcadeGame)
[![TetrisArcadeGame contributors](https://img.shields.io/github/contributors/vives-project-xp/TetrisArcadeGame?style=social&logo=github)](https://github.com/vives-project-xp/TetrisArcadeGame/graphs/contributors)

## Table of Contents
- [Team](#team)
- [Project Overview](#project-overview)
- [Features](#features)
- [Documentation](#documentation)
- [Posters](#posters)
- [Project Structure](#project-structure)

## Team
- [<img src="https://github.com/Danaezutterman.png" alt="" width="25" style="margin-bottom:-6px;">Danae Zutterman](https://github.com/Danaezutterman)
- [<img src="https://github.com/LarsYse.png" alt="" width="25" style="margin-bottom:-6px;">Lars Ysebaert](https://github.com/LarsYse)
- [<img src="https://github.com/finn6698.png" alt="" width="25" style="margin-bottom:-6px;">Finn Van Peteghem](https://github.com/finn6698)
- [<img src="https://github.com/TimoPlts.png" alt="" width="25" style="margin-bottom:-6px;">Timo Plets](https://github.com/TimoPlts)
- [<img src="https://github.com/ondrejkozel.png" alt="" width="25" style="margin-bottom:-6px;">Ondřej Kozel](https://github.com/ondrejkozel)

## Project Overview
This project focuses on the design and realization of a physical Tetris arcade game inside a custom-built housing. The game is displayed in real time on an LED game board and includes a scoreboard and a next-block display. A Raspberry Pi acts as the main controller, handling the physical button inputs while driving the LED matrix and speaker output.

The system is designed as a complete arcade experience rather than only a software project. In addition to the game logic, this repository also contains documentation for the hardware, housing, posters, and Raspberry Pi autostart setup.

## Documentation
- [Documentation overview](./Documentation/README.md) for the full documentation index
- [Architecture](./Documentation/Architecture/README.md) for the electrical and LED diagrams
- [Autostart](./Documentation/Autostart/Autostartscript.md) for the Raspberry Pi `systemd` service setup
- [Housing](./Housing/README.md) for the housing and laser-cutting related files

## Posters
<div style="display: flex; gap: 10px;">
   <img src="Documentation/Posters/New%20Version/Tetris%20Arcade%20game%20poster.png" alt="Tetris Arcade poster" width="350">
   <img src="Documentation/Posters/New%20Version/Tetris%20Arcade%20game%20poster%20EN.png" alt="Tetris Arcade poster in English" width="350">
</div>

## Project Structure
- [Documentation](./Documentation/README.md): project documentation, architecture, autostart, bill of materials, and posters
- [Housing](./Housing/README.md): housing design and related fabrication files
- [Social Media](./Social%20Media): images and videos created for communication and promotion
- [src](./src): source code for the game and LED-related software
