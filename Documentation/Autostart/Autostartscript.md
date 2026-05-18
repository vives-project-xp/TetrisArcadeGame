# Raspberry Pi Autostart Setup

This document explains how the Tetris Arcade game starts automatically when the Raspberry Pi receives power and finishes booting. The setup uses a `systemd` service that launches the Python application in `src/game_console`.

## Overview

The service file used for this project is stored in [tetris.service](./tetris.service). It starts the game from the following location:

- Project folder: `/home/tetris02/TetrisArcadeGame`
- Game folder: `/home/tetris02/TetrisArcadeGame/src/game_console`
- Python executable: `/home/tetris02/TetrisArcadeGame/src/game_console/venv/bin/python`
- Main file: `/home/tetris02/TetrisArcadeGame/src/game_console/main.py`

## 1. Copy the project to the Raspberry Pi

Make sure the repository is present on the Raspberry Pi at:

```bash
/home/tetris02/TetrisArcadeGame
```

If your project is stored in another location or under another user, you must update the paths in the service file.

## 2. Make sure the virtual environment exists

The service starts the game with the Python interpreter inside the virtual environment. Verify that this interpreter exists:

```bash
ls /home/tetris02/TetrisArcadeGame/src/game_console/venv/bin/python
```

If needed, create the virtual environment and install the required packages:

```bash
cd /home/tetris02/TetrisArcadeGame/src/game_console
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Create the `systemd` service

Create a service file, for example:

```bash
sudo nano /etc/systemd/system/tetris.service
```

Add the following configuration. This is the same service definition as in [tetris.service](./tetris.service):

```ini
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
```

## 4. Reload `systemd`

After creating or changing the service file, reload the `systemd` configuration:

```bash
sudo systemctl daemon-reload
```

## 5. Enable the service

Enable the service so it starts automatically after every boot:

```bash
sudo systemctl enable tetris.service
```

## 6. Start the service

Start it manually once to verify the configuration:

```bash
sudo systemctl start tetris.service
```

## 7. Check the service status

Use the following command to confirm that the service is running:

```bash
sudo systemctl status tetris.service
```

If everything is configured correctly, you should see a result similar to:

```text
* tetris.service - Tetris Arcade Game
     Loaded: loaded (/etc/systemd/system/tetris.service; enabled)
     Active: active (running)
     Main PID: 1234 (python)
```

Important things to verify:

- `Loaded: enabled` means the service will start automatically on boot.
- `Active: active (running)` means the game is currently running.
- `Main PID` confirms that the Python process was started by `systemd`.

## 8. Check the logs

If the service does not start correctly, inspect the logs:

```bash
sudo journalctl -u tetris.service -e
```

To follow the logs live:

```bash
sudo journalctl -u tetris.service -f
```

## 9. Test the autostart behavior

Reboot the Raspberry Pi:

```bash
sudo reboot
```

After the Raspberry Pi has started again, check the service once more:

```bash
sudo systemctl status tetris.service
```

If the autostart works correctly, the service should again show:

```text
Active: active (running)
```

This confirms that the Tetris Arcade game starts automatically when the Raspberry Pi powers on.

## Notes

- The current service file uses `User=root`. If you want to run the game as another user, update `User`, `WorkingDirectory`, and `ExecStart` together.
- If the repository path changes, the service file must be updated to match the new location.
- The service definition itself is stored in [tetris.service](./tetris.service) for reference.
