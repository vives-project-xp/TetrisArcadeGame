# Quick Start Guide - 10 Minuten Setup

Deze guide helpt je om zo snel mogelijk aan de slag te gaan.

## Benodigdheden

### Hardware
- ✅ NUCLEO-H533RE board
- ✅ 2x USB kabel (type-A naar micro-USB)
- ✅ Windows PC met USB poorten

### Software (Download eerst!)
- ✅ [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) (Latest version)
- ✅ [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) (Included in CubeIDE)
- ✅ [MIDI-View](http://hautetechnique.com/midi/midiview/)

---

## Optie 1: Snelle Start (Pre-configured)

### Stap 1: Download Project
Kopieer de `STM32_USB_MIDI` folder naar je workspace.

### Stap 2: Open in STM32CubeIDE
1. Open STM32CubeIDE
2. File → Open Projects from File System
3. Select `STM32_USB_MIDI` folder
4. Click **Finish**

### Stap 3: Build & Flash
1. Right-click project → **Build Project** (Ctrl+B)
   - Wacht tot "Build Finished. 0 errors, 0 warnings"
2. Click **Debug** button (groene bug icon) of F11
3. In Debug perspective, click **Resume** (F8) om te starten
4. Stop debugging na 2 seconden (Ctrl+F2)

### Stap 4: Hardware Setup
```
BELANGRIJK: Volg deze volgorde!

1. ⚡ Disconnect ST-Link USB kabel (CN1)
2. 🔧 VERWIJDER JP1 jumper
3. 🔌 Sluit USB kabel aan op CN10 (User USB)
4. ⏰ Wacht 5 seconden voor enumeratie
```

### Stap 5: Verify in Windows
1. Open **Device Manager** (Win+X → Device Manager)
2. Expand "Sound, video and game controllers"
3. Check for **"USB Audio Device"** ✅
   - Als je dit ziet: SUCCESS! Ga naar stap 6
   - Anders: zie [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Stap 6: Test MIDI
1. Open **MIDI-View**
2. Options → MIDI Devices
3. Vink aan: ☑ **STM32 MIDI Device**
4. Click **OK**

### Stap 7: Test Button
1. Druk op **blauwe USER button** (PC13)
2. 💡 Groene LED moet AAN gaan
3. 🎹 MIDI-View toont:
   ```
   Status: 90  Chan: 1  Data1: 60  Data2: 127  [Note On]
   ```
4. Laat button los
5. 💡 LED moet UIT gaan
6. 🎹 MIDI-View toont:
   ```
   Status: 80  Chan: 1  Data1: 60  Data2: 64   [Note Off]
   ```

### ✅ KLAAR!

Als alles werkt, maak screenshots voor je deliverable:
- Screenshot 1: Device Manager met USB Audio Device
- Screenshot 2: MIDI-View device selection
- Screenshot 3: MIDI-View met Note ON/OFF events

---

## Optie 2: Van Scratch (STM32CubeMX)

### Tijdsinschatting: ~30 minuten

#### Stap 1: Nieuw Project in CubeMX
1. Open STM32CubeMX
2. File → New Project
3. Board Selector → NUCLEO-H533RE
4. Start Project → Yes (initialize with default pinout)

#### Stap 2: Clock Configuratie
1. Ga naar **Clock Configuration** tab
2. Configureer:
   ```
   HSE: 8 MHz (Bypass)
   HSI48: Enable
   SYSCLK: 250 MHz (PLL: /M=2, ×N=125, /P=2)
   USB Clock: HSI48 (48 MHz)
   ```
3. Alles moet groen zijn ✅

#### Stap 3: USB Enable
1. Connectivity → **USB** → Mode: **Device_Only**
2. Middleware → **USB_DEVICE** → Class: **Audio**

#### Stap 4: Code Generatie
1. Project → Settings:
   - Project Name: `STM32_USB_MIDI`
   - Toolchain: STM32CubeIDE
2. **Generate Code**
3. **Open Project**

#### Stap 5: Voeg Custom MIDI Code Toe
1. Copy files:
   ```
   Core/Inc/usbd_midi.h        → [Generated]/Core/Inc/
   Core/Src/usbd_midi.c        → [Generated]/Core/Src/
   Core/Src/main.c             → REPLACE [Generated]/Core/Src/main.c
   USB_DEVICE/App/usbd_desc.c  → REPLACE [Generated]/USB_DEVICE/App/usbd_desc.c
   USB_DEVICE/App/usbd_desc.h  → REPLACE [Generated]/USB_DEVICE/App/usbd_desc.h
   ```

2. **Edit** `USB_DEVICE/App/usb_device.c`:
   
   Zoek en vervang:
   ```c
   // Change include
   #include "usbd_audio.h"  →  #include "usbd_midi.h"
   
   // Change class registration
   USBD_RegisterClass(&hUsbDeviceFS, &USBD_AUDIO);
   →
   USBD_RegisterClass(&hUsbDeviceFS, &USBD_MIDI);
   ```

3. **Refresh Project** (F5)
4. **Build** (Ctrl+B)

#### Stap 6: Flash & Test
Volg Stap 3-7 van Optie 1

**Zie [CUBEMX_SETUP.md](CUBEMX_SETUP.md) voor gedetailleerde uitleg**

---

## Common Issues (Snel Oplossen)

### ❌ Device niet herkend
```
CHECK:
☐ JP1 jumper VERWIJDERD?
☐ USB op CN10 (niet CN1)?
☐ Andere USB kabel proberen?
```

### ❌ Build errors
```
ACTION:
1. Project → Clean (Clean all selected)
2. Project → Build (Ctrl+B)
3. Check Console for specific errors
```

### ❌ Geen MIDI messages
```
DEBUG:
1. LED knippert bij button press? 
   → JA: USB probleem
   → NEE: Button/GPIO probleem
   
2. Device in MIDI-View lijst?
   → NEE: Driver/recognition probleem
   → JA: MIDI packet probleem
```

**Voor gedetailleerde troubleshooting**: Zie [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Next Steps

### Begrijpen hoe het werkt
Lees in deze volgorde:
1. [README.md](README.md) - Project overview
2. [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - Hardware details
3. [USB_DESCRIPTOR_EXPLAINED.md](USB_DESCRIPTOR_EXPLAINED.md) - USB MIDI protocol

### Code Understanding
Key files:
- **main.c**: Button handling & MIDI sending
- **usbd_midi.c**: USB MIDI class implementation
- **usbd_desc.c**: USB descriptors

### Experimentation
Probeer deze aanpassingen:
```c
// In main.c - Change note:
USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, MIDI_NOTE_E4, MIDI_VELOCITY_MAX);
//                                      ^^^^^^^^^^^^
// MIDI_NOTE_C4 (60) → MIDI_NOTE_E4 (64)

// Multiple notes sequence:
const uint8_t melody[] = {60, 62, 64, 65, 67};  // C D E F G
for (int i = 0; i < 5; i++) {
  USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, melody[i], 127);
  HAL_Delay(500);
  USBD_MIDI_SendNoteOff(&hUsbDeviceFS, 0, melody[i], 64);
  HAL_Delay(100);
}
```

---

## Deliverable Checklist

Voor je indiening heb je nodig:

### Screenshots (3x VERPLICHT)
- [ ] **Screenshot 1**: Device Manager met USB Audio Device
- [ ] **Screenshot 2**: MIDI-View device selection dialog
- [ ] **Screenshot 3**: MIDI-View met Note ON/OFF messages

### Broncode (met uitleg)
- [ ] **main.c** met comments
- [ ] **usbd_midi.c** met comments (descriptor uitleg)
- [ ] **usbd_midi.h** header file

### Documentatie
- [ ] **README.md** of eigen document met:
  - Hardware setup uitleg (jumpers!)
  - USB MIDI descriptor uitleg
  - Gebruikte library (STM32 USB Device Middleware)
  - Test resultaten

### Template:
```markdown
# STM32H533RE USB MIDI Device

## Hardware Configuratie
- JP1: VERWIJDERD (voor USB voeding)
- USB connector: CN10 (User USB)
- Button: PC13, LED: PA5

## USB MIDI Descriptor
De descriptor bestaat uit:
1. Device Descriptor (VID: 0x0483, PID: 0x5740)
2. Configuration Descriptor (2 interfaces)
3. Audio Control Interface (verplicht voor MIDI)
4. MIDI Streaming Interface met embedded jacks
5. Bulk IN/OUT endpoints (64 bytes)

[Voeg USB_DESCRIPTOR_EXPLAINED.md toe voor details]

## Gebruikte Library
STM32 USB Device Middleware met custom MIDI class implementatie

## Test Resultaten
[Screenshot 1: Device Manager]
[Screenshot 2: MIDI-View selection]
[Screenshot 3: MIDI messages]

Device correct herkend als USB MIDI. 
Note ON/OFF messages succesvol verstuurd.

## Broncode
Zie bijgevoegde files...
```

---

## Timeline Estimate

| Fase | Tijd | Actie |
|------|------|-------|
| Setup | 5 min | Download software, hardware setup |
| Build | 3 min | Open project, build, flash |
| Hardware | 2 min | Jumper config, USB reconnect |
| Test | 5 min | Device Manager, MIDI-View test |
| Screenshots | 3 min | Capture evidence |
| Document | 15 min | Write explanations |
| **TOTAL** | **~30 min** | Full working demo |

---

## Support

**Stuck? Check in deze volgorde:**

1. ⚡ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 90% van problemen
2. 📖 [README.md](README.md) - Project overview
3. 🔧 [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - Jumper settings
4. 🎓 [CUBEMX_SETUP.md](CUBEMX_SETUP.md) - Configuration details
5. 💬 **Vraag docent** - Als niets anders werkt

---

## Success Criteria

✅ Je bent klaar als:
- [ ] Device herkend als "USB Audio Device"
- [ ] MIDI-View toont "STM32 MIDI Device"
- [ ] Button press → LED ON → MIDI Note ON (90 01 3C 7F)
- [ ] Button release → LED OFF → MIDI Note OFF (80 01 3C 40)
- [ ] 3 screenshots gemaakt
- [ ] Broncode met uitleg klaar

🎉 **Gefeliciteerd! Je hebt je eigen USB MIDI controller gemaakt!**

---

## Bonus Challenges (Optioneel)

1. **Velocity Control**: Gebruik ADC om velocity te variëren
2. **Multiple Notes**: Verschillende notes op verschillende pins
3. **MIDI IN**: Ontvang MIDI van host (LED control)
4. **Sequencer**: Automatische note sequence afspelen
5. **SysEx Messages**: Custom device configuration via MIDI

Veel succes! 🚀
