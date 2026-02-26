# STM32H533RE USB MIDI Device - Complete Project

## 📋 Project Summary

Dit project implementeert een **USB MIDI Class Device** op de STM32H533RE Nucleo-board. Het device wordt door de computer herkend als een standaard MIDI device en kan MIDI Note ON/OFF berichten versturen via USB zonder speciale drivers.

### Functionaliteit
- ✅ USB MIDI Class compliant (USB Audio subclass)
- ✅ Plug-and-play (geen driver installatie nodig)
- ✅ Note ON/OFF messages via button press
- ✅ LED feedback bij MIDI activiteit
- ✅ USB-powered (geen externe voeding)

### Hardware
- **Board**: NUCLEO-H533RE
- **MCU**: STM32H533RET6 (Cortex-M33, 250 MHz, 512KB Flash, 256KB RAM)
- **Jumpers**: JP1 verwijderd (voor USB power via CN10)
- **USB**: CN10 (User USB connector)
- **Input**: PC13 (Blue User Button)
- **Output**: PA5 (Green LED)

---

## 📚 Documentatie Index

Start hier voor je gebruik case:

### 🚀 Ik wil snel beginnen
**→ [QUICK_START.md](QUICK_START.md)**
- 10-minuten setup guide
- Pre-configured project gebruiken
- Build, flash, en test in 30 minuten

### 🔧 Ik wil het zelf configureren
**→ [CUBEMX_SETUP.md](CUBEMX_SETUP.md)**
- Stap-voor-stap STM32CubeMX configuratie
- Clock setup (250 MHz SYSCLK, 48 MHz USB)
- Pinout en peripheral configuratie
- Code generatie en integratie

### ⚙️ Hardware setup uitleg
**→ [HARDWARE_SETUP.md](HARDWARE_SETUP.md)**
- Jumper configuratie (JP1, JP2)
- CN1 vs CN10 USB connectors
- Power management
- Pinout details

### 🎵 USB MIDI protocol begrijpen
**→ [USB_DESCRIPTOR_EXPLAINED.md](USB_DESCRIPTOR_EXPLAINED.md)**
- Complete descriptor breakdown
- Device, Configuration, Interface, Endpoint descriptors
- MIDI Jack configuratie
- USB MIDI packet format
- Code Index Numbers (CIN)

### 🧪 Testen en verificatie
**→ [TESTING_GUIDE.md](TESTING_GUIDE.md)**
- MIDI-View installatie en setup
- Device Manager verificatie
- Screenshot requirements voor deliverable
- Note ON/OFF testing
- Advanced debugging (Wireshark, USBPcap)

### 🐛 Problemen oplossen
**→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
- Device recognition problems
- USB communication issues
- MIDI message problems
- Hardware debugging
- Software/build errors
- Checklist en flowcharts

### 📖 Gedetailleerde uitleg
**→ [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md)**
- Architectuur overview
- Code walk-through (main.c, usbd_midi.c)
- Clock configuration uitleg
- Memory layout
- Library vergelijking
- Future improvements

### 📝 Project overview
**→ [README.md](README.md)**
- High-level project beschrijving
- Vereisten en setup
- Project structuur
- USB MIDI basics
- Referenties

---

## 📁 File Structure

```
STM32_USB_MIDI/
│
├── 📄 README.md                      # Project overview
├── 📄 QUICK_START.md                 # Snelle setup guide (START HIER!)
├── 📄 PROJECT_EXPLANATION.md         # Gedetailleerde code uitleg
├── 📄 CUBEMX_SETUP.md                # STM32CubeMX configuratie
├── 📄 HARDWARE_SETUP.md              # Hardware jumper settings
├── 📄 USB_DESCRIPTOR_EXPLAINED.md    # USB MIDI protocol deep dive
├── 📄 TESTING_GUIDE.md               # Test procedures & screenshots
├── 📄 TROUBLESHOOTING.md             # Debug guide
│
├── Core/
│   ├── Inc/
│   │   ├── main.h                    # Main header
│   │   └── usbd_midi.h               # USB MIDI class header
│   │
│   └── Src/
│       ├── main.c                    # Main application (button → MIDI)
│       └── usbd_midi.c               # USB MIDI class implementation
│
├── USB_DEVICE/
│   ├── App/
│   │   ├── usbd_desc.h               # USB descriptor header
│   │   ├── usbd_desc.c               # USB descriptors (VID/PID/Strings)
│   │   └── usb_device.c              # USB device initialization
│   │
│   └── Target/
│       └── usbd_conf.c               # USB configuration
│
└── Drivers/                          # STM32 HAL drivers (gegenereerd)
    ├── STM32H5xx_HAL_Driver/
    └── CMSIS/
```

---

## 🎯 Voor de Opdracht

### Deliverables Checklist

#### ✅ Screenshots (3x VERPLICHT)

1. **Device Manager**
   - Windows Device Manager met "USB Audio Device" zichtbaar
   - Properties tonen VID/PID (0x0483/0x5740)
   - Locatie: Sound, video and game controllers

2. **MIDI-View Device Selection**
   - MIDI Devices dialog
   - "STM32 MIDI Device" in lijst
   - Checkbox aangevinkt

3. **MIDI Messages**
   - MIDI-View main window
   - Minimum 2x Note ON events
   - Minimum 2x Note OFF events
   - Timestamps, status, channel, note, velocity zichtbaar

📸 **Zie [TESTING_GUIDE.md](TESTING_GUIDE.md)** voor screenshot voorbeelden

#### ✅ Broncode met Uitleg

**Belangrijkste files**:
- `Core/Src/main.c` - Application logic
- `Core/Src/usbd_midi.c` - USB MIDI implementation
- `Core/Inc/usbd_midi.h` - MIDI constants en prototypes
- `USB_DEVICE/App/usbd_desc.c` - USB descriptors

**Voeg comments toe die uitleggen**:
- Jumper configuratie (JP1 verwijderd)
- USB clock settings (48 MHz)
- USB descriptor structuur
- MIDI packet format
- Button debouncing

#### ✅ Schriftelijke Uitleg

**Minimum topics te behandelen**:

1. **Hardware configuratie**
   - Jumper settings (JP1, JP2)
   - USB connector (CN10 vs CN1)
   - Power source (USB VBUS)

2. **USB MIDI Descriptor**
   - Device Descriptor (VID/PID)
   - Configuration Descriptor (interfaces)
   - MIDI Streaming Interface
   - Embedded MIDI Jacks
   - Bulk endpoints

3. **Gebruikte Library**
   - STM32 USB Device Middleware
   - Custom MIDI class implementation
   - HAL (Hardware Abstraction Layer)

4. **Test Resultaten**
   - Device recognition success
   - MIDI messages received
   - Note values correct (60 = Middle C)

📖 **Gebruik [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md)** als basis

---

## 🔍 Wat heb je uitgezocht?

### 1. Device configureren voor USB?

**Antwoord gevonden in**: [CUBEMX_SETUP.md](CUBEMX_SETUP.md)

- **USB Peripheral**: Connectivity → USB → Device_Only
- **Clock**: 48 MHz exact (HSI48 of PLL)
- **Pins**: PA11 (USB_DM), PA12 (USB_DP)
- **Middleware**: USB_DEVICE met Audio class (aangepast naar MIDI)

### 2. Externe library voor MIDI?

**Antwoord gevonden in**: [README.md](README.md) en [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md)

- **Primary**: STM32 USB Device Middleware (HAL-based)
- **Custom**: Eigen USB MIDI class implementatie (usbd_midi.c)
- **Alternatieven**: TinyUSB, libusb_stm32 (niet gebruikt)

**Waarom eigen implementatie?**
- USB Device library biedt framework
- MIDI class niet standaard in STM32Cube
- Custom class geeft volledige controle

### 3. Jumper-instellingen voor USB-voeding?

**Antwoord gevonden in**: [HARDWARE_SETUP.md](HARDWARE_SETUP.md)

```
JP1: VERWIJDERD (disconnect ST-Link power)
JP2: Geplaatst (ON positie voor normale werking)
USB: CN10 (User USB connector met VBUS)
```

**Waarom JP1 verwijderen?**
- Voorkomt power conflict tussen ST-Link en USB User
- Nucleo heeft twee power sources: ST-Link (CN1) en USB User (CN10)
- Voor USB device moet het via CN10 gevoed worden

### 4. USB MIDI descriptor structuur?

**Antwoord gevonden in**: [USB_DESCRIPTOR_EXPLAINED.md](USB_DESCRIPTOR_EXPLAINED.md)

**Hiërarchie**:
```
Device Descriptor (18 bytes)
  └─ Configuration Descriptor (9 bytes)
      ├─ Audio Control Interface (18 bytes)
      │   └─ AC Header (verplicht, geen functionaliteit)
      │
      └─ MIDI Streaming Interface (74 bytes)
          ├─ MS Header (7 bytes)
          ├─ MIDI Jacks (4x, 6-9 bytes each)
          │   ├─ IN Jack Embedded (ID:1)
          │   ├─ IN Jack External (ID:2)
          │   ├─ OUT Jack Embedded (ID:3)
          │   └─ OUT Jack External (ID:4)
          │
          └─ Endpoints (2x, 14 bytes each)
              ├─ Bulk OUT (Host → Device)
              └─ Bulk IN (Device → Host)

Total: 101 bytes
```

**Key details**:
- **bInterfaceClass**: 0x01 (Audio)
- **bInterfaceSubClass**: 0x03 (MIDI Streaming)
- **Endpoint Type**: Bulk (0x02)
- **Max Packet Size**: 64 bytes
- **MIDI Packet**: 4 bytes (CIN + 3 MIDI bytes)

---

## 💡 Tips voor Presentatie/Verslag

### Structuur Suggestie

1. **Inleiding**
   - Doel: STM32 als USB MIDI device
   - Hardware: Nucleo-H533RE
   - Software: STM32CubeIDE + HAL + Custom MIDI class

2. **Hardware Setup**
   - Jumper configuratie (JP1 removed!)
   - Power via USB
   - Screenshot van board met annotations

3. **Software Architectuur**
   - Diagram: Hardware → HAL → USB Middleware → MIDI Class → Application
   - Clock configuratie (48 MHz USB clock)
   - Code structure

4. **USB MIDI Implementatie**
   - Descriptor uitleg (beste met diagram van USB_DESCRIPTOR_EXPLAINED.md)
   - MIDI packet format
   - Code snippets met uitleg

5. **Resultaten**
   - Screenshots (Device Manager, MIDI-View)
   - Bewijs van correcte werking
   - Note ON/OFF messages

6. **Conclusie**
   - Vereisten behaald
   - Lessons learned
   - Mogelijke uitbreidingen

### Visuele Aids

- ✅ Jumper configuratie foto/diagram
- ✅ USB descriptor diagram (hierarchie)
- ✅ Data flow diagram (Button → MIDI packet → Host)
- ✅ Screenshot annotaties (highlight belangrijke info)

### Code Snippets

**Toon deze key sections**:

1. **USB MIDI Packet Construction** (usbd_midi.c):
```c
midi_packet[0] = (MIDI_CIN_NOTE_ON << 4) | (channel & 0x0F);
midi_packet[1] = MIDI_STATUS_NOTE_ON | (channel & 0x0F);
midi_packet[2] = note & 0x7F;
midi_packet[3] = velocity & 0x7F;
```

2. **Button Debouncing** (main.c):
```c
if ((HAL_GetTick() - last_debounce_time) > debounce_delay) {
  // State stable, act on button change
}
```

3. **USB Descriptor** (usbd_midi.c):
```c
// MIDI Streaming Interface
0x09, 0x04, 0x01, 0x00, 0x02, 0x01, 0x03, 0x00, 0x00,
//    ^Interface   ^2 EPs  ^Audio ^MIDI Streaming
```

---

## 🚀 Next Steps

### Als je klaar bent met de basis opdracht:

1. **Verificatie**
   - [ ] 3 screenshots gemaakt en opgeslagen
   - [ ] Code met comments klaar
   - [ ] Documentatie geschreven
   - [ ] Alles getest en werkend

2. **Optionele uitbreidingen** (voor extra punten/leerervaring):
   - [ ] MIDI IN implementatie (ontvang van host)
   - [ ] Multiple notes (verschillende buttons/pins)
   - [ ] ADC velocity sensing (druk-gevoelig)
   - [ ] CC (Control Change) messages
   - [ ] LED matrix voor MIDI visualisatie

3. **Presentatie voorbereiden**
   - [ ] Slides maken
   - [ ] Demo voorbereiden (live of video)
   - [ ] Antwoorden voorbereiden op mogelijke vragen

---

## 📞 Support

### Als je vastloopt:

1. **Check TROUBLESHOOTING.md eerst**
   - 90% van problemen staan daar

2. **Verify Basics**
   ```
   ☐ JP1 removed?
   ☐ USB on CN10?
   ☐ Firmware flashed successfully?
   ☐ LED blinks (firmware running)?
   ```

3. **Read Error Messages**
   - Device Manager errors → USB enumeration probleem
   - Build errors → Missing files/includes
   - MIDI-View geen data → Endpoint/packet probleem

4. **Vraag Hulp**
   - Docent/TA
   - Classmates
   - ST Community Forum

**Provide deze info bij vragen**:
- Screenshots van error
- STM32CubeIDE version
- What you tried already

---

## ✅ Success Criteria

Je bent klaar als:

### Hardware
- [x] Nucleo-H533RE correct geconfigureerd (JP1 removed)
- [x] USB kabel op CN10 (User USB)
- [x] Device powered via USB (geen ST-Link)

### Software
- [x] Project builds zonder errors
- [x] Firmware successfully geflashed
- [x] LED blinks bij button press

### USB Recognition
- [x] Device Manager toont "USB Audio Device"
- [x] VID/PID = 0x0483/0x5740
- [x] Geen "Unknown Device" errors

### MIDI Functionality
- [x] MIDI-View ziet "STM32 MIDI Device"
- [x] Button press → Note ON (90 01 3C 7F)
- [x] Button release → Note OFF (80 01 3C 40)
- [x] Consistent, reliable operation

### Deliverables
- [x] 3 screenshots (Device Manager, MIDI-View selection, Messages)
- [x] Source code met comments/uitleg
- [x] Written documentation (hardware, USB, library, results)

---

## 🎉 Gefeliciteerd!

Als alle checkboxes ✅ zijn, heb je succesvol:
- Een STM32 microcontroller geconfigureerd als USB MIDI device
- USB protocol en descriptors begrepen
- MIDI protocol geïmplementeerd
- Hardware configuratie (jumpers, power) beheerst
- Debugging en testing skills ontwikkeld

**Je hebt nu de basis kennis voor**:
- Andere USB device classes (HID, CDC, MSC)
- Custom USB devices ontwerpen
- MIDI controllers bouwen
- Embedded USB ontwikkeling

**Veel succes met je project! 🚀🎵**

---

## 📎 Quick Links

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [QUICK_START.md](QUICK_START.md) | 10-min setup | First time setup |
| [CUBEMX_SETUP.md](CUBEMX_SETUP.md) | STM32CubeMX config | Creating from scratch |
| [HARDWARE_SETUP.md](HARDWARE_SETUP.md) | Jumper settings | Hardware questions |
| [USB_DESCRIPTOR_EXPLAINED.md](USB_DESCRIPTOR_EXPLAINED.md) | USB protocol | Understanding descriptors |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Test procedures | Verification & screenshots |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Debug guide | When things don't work |
| [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md) | Code walk-through | Understanding implementation |
| [README.md](README.md) | Overview | General reference |

---

**Project Version**: 1.0  
**Last Updated**: February 2026  
**STM32CubeH5**: v1.3.0  
**Target**: NUCLEO-H533RE (STM32H533RET6)

Voor vragen of feedback: zie je docent of TA.
