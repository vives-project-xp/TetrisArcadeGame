[Unit]
Description=Tetris Arcade Game
After=multi-user.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/tetris02/TetrisArcadeGame/src/game_console
ExecStart=/home/tetris02/TetrisArcadeGame/src/game_console/venv/bin/python /home/tetris02/TetrisArcadeGame/src/game_console/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target