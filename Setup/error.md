~~~^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/console/seven_segment.py", line 17, in __init__
May 07 09:47:35 tetris-arcade python[4120]:     self.__init_hardware(config.SEVEN_SEGMENT_I2C_ADDRESS)
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/console/seven_segment.py", line 24, in __init_hardware
May 07 09:47:35 tetris-arcade python[4120]:     self.__led = HT16K33SegmentBig(i2c, i2c_address=i2c_address)
May 07 09:47:35 tetris-arcade python[4120]:                  ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33segmentbig.py", line 41, in __init__
May 07 09:47:35 tetris-arcade python[4120]:     super(HT16K33SegmentBig, self).__init__(i2c, i2c_address)
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 35, in __init__
May 07 09:47:35 tetris-arcade python[4120]:     self.power_on()
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 95, in power_on
May 07 09:47:35 tetris-arcade python[4120]:     self._write_cmd(self.HT16K33_GENERIC_SYSTEM_ON)
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 120, in _write_cmd
May 07 09:47:35 tetris-arcade python[4120]:     self.i2c.writeto(self.address, bytes([byte]))
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/busio.py", line 223, in writeto
May 07 09:47:35 tetris-arcade python[4120]:     return self._i2c.writeto(address, buffer, stop=True)
May 07 09:47:35 tetris-arcade python[4120]:            ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/adafruit_blinka/microcontroller/generic_linux/i2c.py", line 60, in writeto
May 07 09:47:35 tetris-arcade python[4120]:     self._i2c_bus.write_bytes(address, buffer[start:end])
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:35 tetris-arcade python[4120]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/Adafruit_PureIO/smbus.py", line 303, in write_bytes
May 07 09:47:35 tetris-arcade python[4120]:     self._device.write(buf)
May 07 09:47:35 tetris-arcade python[4120]:     ~~~~~~~~~~~~~~~~~~^^^^^
May 07 09:47:35 tetris-arcade python[4120]: OSError: [Errno 5] Input/output error
May 07 09:47:35 tetris-arcade systemd[1]: tetris.service: Main process exited, code=exited, status=1/FAILURE
May 07 09:47:35 tetris-arcade systemd[1]: tetris.service: Failed with result 'exit-code'.
May 07 09:47:40 tetris-arcade systemd[1]: tetris.service: Scheduled restart job, restart counter is at 209.
May 07 09:47:40 tetris-arcade systemd[1]: Started tetris.service - Tetris Arcade Game.
May 07 09:47:40 tetris-arcade python[4130]: pygame 2.6.1 (SDL 2.28.4, Python 3.13.5)
May 07 09:47:40 tetris-arcade python[4130]: Hello from the pygame community. https://www.pygame.org/contribute.html
May 07 09:47:40 tetris-arcade python[4130]: Traceback (most recent call last):
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/main.py", line 14, in <module>
May 07 09:47:40 tetris-arcade python[4130]:     main()
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/main.py", line 8, in main
May 07 09:47:40 tetris-arcade python[4130]:     console = GameConsole()
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/console/game_console.py", line 27, in __init__
May 07 09:47:40 tetris-arcade python[4130]:     self.__seven_segment = SevenSegment()
May 07 09:47:40 tetris-arcade python[4130]:                            ~~~~~~~~~~~~^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/console/seven_segment.py", line 17, in __init__
May 07 09:47:40 tetris-arcade python[4130]:     self.__init_hardware(config.SEVEN_SEGMENT_I2C_ADDRESS)
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/console/seven_segment.py", line 24, in __init_hardware
May 07 09:47:40 tetris-arcade python[4130]:     self.__led = HT16K33SegmentBig(i2c, i2c_address=i2c_address)
May 07 09:47:40 tetris-arcade python[4130]:                  ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33segmentbig.py", line 41, in __init__
May 07 09:47:40 tetris-arcade python[4130]:     super(HT16K33SegmentBig, self).__init__(i2c, i2c_address)
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 35, in __init__
May 07 09:47:40 tetris-arcade python[4130]:     self.power_on()
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 95, in power_on
May 07 09:47:40 tetris-arcade python[4130]:     self._write_cmd(self.HT16K33_GENERIC_SYSTEM_ON)
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/ht16k33/ht16k33.py", line 120, in _write_cmd
May 07 09:47:40 tetris-arcade python[4130]:     self.i2c.writeto(self.address, bytes([byte]))
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/busio.py", line 223, in writeto
May 07 09:47:40 tetris-arcade python[4130]:     return self._i2c.writeto(address, buffer, stop=True)
May 07 09:47:40 tetris-arcade python[4130]:            ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/adafruit_blinka/microcontroller/generic_linux/i2c.py", line 60, in writeto
May 07 09:47:40 tetris-arcade python[4130]:     self._i2c_bus.write_bytes(address, buffer[start:end])
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
May 07 09:47:40 tetris-arcade python[4130]:   File "/home/tetris02/TetrisArcadeGame/src/game_console/venv/lib/python3.13/site-packages/Adafruit_PureIO/smbus.py", line 303, in write_bytes
May 07 09:47:40 tetris-arcade python[4130]:     self._device.write(buf)
May 07 09:47:40 tetris-arcade python[4130]:     ~~~~~~~~~~~~~~~~~~^^^^^
May 07 09:47:40 tetris-arcade python[4130]: OSError: [Errno 5] Input/output error
May 07 09:47:40 tetris-arcade systemd[1]: tetris.service: Main process exited, code=exited, status=1/FAILURE
