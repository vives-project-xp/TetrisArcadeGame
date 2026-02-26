# STM32H533RE USB MIDI Device Project

## Overzicht
Dit project configureert de Nucleo-H533RE als een USB MIDI Class device dat MIDI note-ON en note-OFF berichten kan versturen.

## Hardware Configuratie

### Jumper Instellingen voor USB Voeding
Voor het gebruik van USB-voeding (zonder ST-Link) op de Nucleo-H533RE:

1. **JP1 (Power Selection)**:
   - Verwijder de jumper van JP1 (disconnect ST-Link power)
   
2. **JP2 (IDD Measurement)**:
   - Plaats jumper op JP2 (ON positie) voor normale werking
   
3. **USB Connector**:
   - Gebruik de **USB User (CN10)** connector (niet de ST-Link USB)
   - Deze is gelabeld als "USB PWR" op het bord

### Pinout voor USB
- **PA11**: USB_DM (USB Data Minus)
- **PA12**: USB_DP (USB Data Plus)
- **USB VBUS**: Voeding via USB connector

## Software Configuratie

### Benodigde Tools
1. **STM32CubeIDE** of **STM32CubeMX**
2. **MIDI-View** of **MIDI-OX** voor Windows
3. **STM32CubeH5** HAL library

### STM32CubeMX Configuratie

#### 1. Clock Configuration
- HSE: Crystal/Ceramic Resonator (8 MHz)
- SYSCLK: 250 MHz (maximaal voor H533RE)
- USB Clock: 48 MHz (verplicht voor USB)
  - Configureer PLL om 48 MHz voor USB clock te genereren

#### 2. USB Device Configuratie
```
Connectivity → USB:
  - Mode: Device_Only
  - Parameter Settings:
    - Device Speed: Full Speed (12 Mb/s)
    - VBUS Sensing: Disabled (of Enabled als je VBUS pin gebruikt)
```

#### 3. GPIO Configuration
- PA11: USB_DM
- PA12: USB_DP
- (Optioneel) PC13: User Button voor MIDI trigger

#### 4. Middleware Configuration
```
Middleware → USB_DEVICE:
  - Class For FS IP: Custom Human Interface Device Class (HID)
  - Opmerking: We passen dit aan naar MIDI in de code
```

## Project Structuur

```
STM32_USB_MIDI/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   └── usb_midi.h
│   └── Src/
│       ├── main.c
│       └── usb_midi.c
├── USB_DEVICE/
│   ├── App/
│   │   ├── usbd_desc.c          # USB Device Descriptors
│   │   ├── usbd_desc.h
│   │   └── usb_device.c
│   └── Target/
│       └── usbd_conf.c
├── Drivers/                      # STM32 HAL Drivers
└── README.md
```

## USB MIDI Descriptor Uitleg

Een USB MIDI device vereist specifieke descriptors:

### Device Descriptor
- bDeviceClass: 0x00 (defined in interface)
- bDeviceSubClass: 0x00
- bDeviceProtocol: 0x00
- idVendor: 0x0483 (STMicroelectronics)
- idProduct: 0x5740 (custom)

### Configuration Descriptor
- Audio Control Interface (bInterfaceClass: 0x01, bInterfaceSubClass: 0x01)
- MIDI Streaming Interface (bInterfaceClass: 0x01, bInterfaceSubClass: 0x03)

### MIDI Streaming Endpoints
- Bulk OUT endpoint (Host → Device)
- Bulk IN endpoint (Device → Host)

## MIDI Message Formaat

USB MIDI packets zijn 4 bytes:
```
Byte 0: Cable Number (4 bits) + Code Index Number (4 bits)
Byte 1: MIDI Status
Byte 2: MIDI Data 1
Byte 3: MIDI Data 2
```

### Note ON Message
```
0x09: Note ON code index
0x90: Channel 1 Note ON status
0x3C: Note number (Middle C = 60 = 0x3C)
0x7F: Velocity (127 = max)
```

### Note OFF Message
```
0x08: Note OFF code index
0x80: Channel 1 Note OFF status
0x3C: Note number
0x40: Velocity (64)
```

## Gebruik

### Compileren en Flashen
1. Open het project in STM32CubeIDE
2. Build het project (Ctrl+B)
3. Flash via ST-Link (Run → Debug of Run)
4. **Disconnect ST-Link na flashen**
5. Configureer jumpers voor USB voeding
6. Sluit USB kabel aan op CN10 (User USB)

### Testen
1. Open MIDI-View of MIDI-OX
2. Selecteer "STM32 MIDI Device" in de MIDI input lijst
3. Druk op de User Button (PC13) op het bord
4. Je zou MIDI Note ON/OFF berichten moeten zien in de software

## Troubleshooting

### Device wordt niet herkend
- Controleer jumper instellingen (JP1 verwijderd)
- Controleer of USB kabel op CN10 zit (niet CN1)
- Controleer USB clock configuratie (moet 48 MHz zijn)
- Installeer eventueel STM32 Virtual COM Port driver

### Geen MIDI berichten ontvangen
- Controleer in Device Manager of device als "USB Audio Device" verschijnt
- Herstart MIDI-View na aansluiten van device
- Controleer of MIDI IN endpoint correct geconfigureerd is

## Externe Libraries

Dit project gebruikt:
- **STM32 HAL Library**: Voor hardware abstractie
- **USB Device Library**: Onderdeel van STM32Cube
- **Custom USB MIDI Class**: Geïmplementeerd in usbd_midi.c

Er zijn ook third-party opties:
- **TinyUSB**: Moderne USB stack met MIDI support
- **libusb_stm32**: Lightweight USB library

## Referenties

- [USB MIDI Specification v1.0](https://www.usb.org/sites/default/files/midi10.pdf)
- [STM32H533RE Reference Manual](https://www.st.com/resource/en/reference_manual/rm0492-stm32h533-stm32h523-and-stm32h562-armbased-32bit-mcus-stmicroelectronics.pdf)
- [Nucleo-H533RE User Manual](https://www.st.com/resource/en/user_manual/um3186-stm32h5-nucleo64-board-mb1813-stmicroelectronics.pdf)

## Author
Project Experience 2.2 International
Vives - Fase 2 - Semester 2
