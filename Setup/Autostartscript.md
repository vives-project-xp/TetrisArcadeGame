# Raspberry Pi Autostart Setup

This document explains how the Tetris Arcade Python script automatically starts when the Raspberry Pi boots.

## 1. Create the Python test script

Example script:

```python
from datetime import datetime

with open("/home/tetris01/Testauto/bootlog.txt", "a") as f:
    f.write("BOOT DETECTED: " + str(datetime.now()) + "\n")
```

## 2. Create a systemd service

Create the service file:

```bash
sudo nano /etc/systemd/system/testboot.service
```

Add the following:

```INI
[Unit]
Description=Tetris Boot Script
After=multi-user.target

[Service]
Type=simple
User=tetris01
WorkingDirectory=/home/tetris01
ExecStart=/usr/bin/python3 /home/tetris01/Testauto/boottest.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 3. Reload systemd

```bash
sudo systemctl daemon-reload
```

## 4. Enable the service

```bash
sudo systemctl enable testboot.service
```

## 5. Start the service

```bash
sudo systemctl start testboot.service
```

## 6. Check the service

```bash
sudo systemctl status testboot.service
```

If the service is configured correctly, you should see something similar to:
```
● testboot.service - Test Boot Script
     Loaded: loaded (/etc/systemd/system/testboot.service; enabled)
     Active: active (running)
     Main PID: 1234 (python3)
```

Important things to check:
- Loaded: enabled → the service will start automatically on boot
- Active: active (running) → the Python script is currently running
- Main PID: python3 → confirms the Python script is running

## 7. Test autostart

```bash
sudo reboot
```

After the Raspberry Pi has started again, check if the service is running:

```bash
sudo systemctl status testboot.service
```

If the autostart works correctly, you should again see:

```
Active: active (running)
```

This confirms that the Python script started automatically during boot.
