# USB MIDI Descriptor Deep Dive

## Wat is een USB Descriptor?

USB Descriptors zijn data structuren die een USB device gebruikt om zichzelf te identificeren en te beschrijven aan de host computer. Ze vertellen de host:
- Wat voor soort device dit is
- Welke functionaliteit het heeft
- Hoe communicatie moet verlopen

## Hierarchie van USB Descriptors

```
Device Descriptor (1x)
    └─ Configuration Descriptor (1x)
        └─ Interface Descriptor (1x of meer)
            ├─ Class-Specific Descriptors
            └─ Endpoint Descriptor (0x of meer)
```

---

## 1. Device Descriptor

Dit is de "root" van het device en bevat globale informatie.

### Structuur (18 bytes):

```c
struct USB_Device_Descriptor {
    uint8_t  bLength;            // 18
    uint8_t  bDescriptorType;    // 0x01 (DEVICE)
    uint16_t bcdUSB;             // USB versie (0x0200 = USB 2.0)
    uint8_t  bDeviceClass;       // Device class
    uint8_t  bDeviceSubClass;    // Device subclass
    uint8_t  bDeviceProtocol;    // Device protocol
    uint8_t  bMaxPacketSize0;    // Max packet size voor endpoint 0
    uint16_t idVendor;           // Vendor ID
    uint16_t idProduct;          // Product ID
    uint16_t bcdDevice;          // Device release number
    uint8_t  iManufacturer;      // Index of manufacturer string
    uint8_t  iProduct;           // Index of product string
    uint8_t  iSerialNumber;      // Index of serial number string
    uint8_t  bNumConfigurations; // Number of configurations
};
```

### Voor ons MIDI Device:

```c
0x12,                     // bLength: 18 bytes
0x01,                     // bDescriptorType: DEVICE
0x00, 0x02,               // bcdUSB: USB 2.0
0x00,                     // bDeviceClass: 0 = Defined in interface
0x00,                     // bDeviceSubClass: 0
0x00,                     // bDeviceProtocol: 0
0x40,                     // bMaxPacketSize0: 64 bytes
0x83, 0x04,               // idVendor: 0x0483 (STMicroelectronics)
0x40, 0x57,               // idProduct: 0x5740 (Custom MIDI)
0x00, 0x02,               // bcdDevice: 2.00
0x01,                     // iManufacturer: String index 1
0x02,                     // iProduct: String index 2
0x03,                     // iSerialNumber: String index 3
0x01,                     // bNumConfigurations: 1
```

**Belangrijke punten**:
- **bDeviceClass = 0x00**: Class wordt gedefinieerd in Interface Descriptor (verplicht voor composite devices)
- **idVendor = 0x0483**: Dit is STMicroelectronics' officiële VID
- **idProduct = 0x5740**: Custom PID (je mag dit gebruiken voor development)

---

## 2. Configuration Descriptor

Beschrijft een specifieke configuratie van het device.

### Structuur (9 bytes):

```c
struct USB_Configuration_Descriptor {
    uint8_t  bLength;             // 9
    uint8_t  bDescriptorType;     // 0x02 (CONFIGURATION)
    uint16_t wTotalLength;        // Totale lengte van alle descriptors
    uint8_t  bNumInterfaces;      // Aantal interfaces
    uint8_t  bConfigurationValue; // Configuration ID
    uint8_t  iConfiguration;      // String descriptor index
    uint8_t  bmAttributes;        // Attributes (self-powered, etc.)
    uint8_t  bMaxPower;           // Max power in 2mA units
};
```

### Voor ons MIDI Device:

```c
0x09,                     // bLength: 9 bytes
0x02,                     // bDescriptorType: CONFIGURATION
0x65, 0x00,               // wTotalLength: 101 bytes (0x0065)
0x02,                     // bNumInterfaces: 2 (Audio Control + MIDI Streaming)
0x01,                     // bConfigurationValue: 1
0x00,                     // iConfiguration: 0 (no string)
0xC0,                     // bmAttributes: Self-powered, no remote wakeup
0x32,                     // bMaxPower: 100mA (50 * 2mA)
```

**Belangrijke punten**:
- **wTotalLength = 101**: Som van alle descriptors in deze configuratie
- **bNumInterfaces = 2**: Audio Control + MIDI Streaming
- **bmAttributes**:
  - Bit 7: Moet altijd 1 zijn (reserved)
  - Bit 6: Self-powered (1 = ja)
  - Bit 5: Remote wakeup (0 = nee)

---

## 3. Interface Descriptors

USB MIDI vereist **twee interfaces**:
1. **Audio Control Interface** (verplicht maar inactief)
2. **MIDI Streaming Interface** (daadwerkelijke MIDI functionaliteit)

### 3.1 Audio Control Interface

```c
// Standard Interface Descriptor
0x09,                     // bLength: 9 bytes
0x04,                     // bDescriptorType: INTERFACE
0x00,                     // bInterfaceNumber: 0
0x00,                     // bAlternateSetting: 0
0x00,                     // bNumEndpoints: 0 (geen data endpoints)
0x01,                     // bInterfaceClass: AUDIO (0x01)
0x01,                     // bInterfaceSubClass: AUDIO_CONTROL (0x01)
0x00,                     // bInterfaceProtocol: 0
0x00,                     // iInterface: 0

// Class-Specific AC Interface Header
0x09,                     // bLength: 9 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x01,                     // bDescriptorSubtype: HEADER
0x00, 0x01,               // bcdADC: Audio Device Class v1.0
0x09, 0x00,               // wTotalLength: 9 bytes
0x01,                     // bInCollection: 1 streaming interface
0x01,                     // baInterfaceNr(1): Interface 1
```

**Uitleg**:
- Deze interface is verplicht voor USB Audio compliance
- Heeft **geen endpoints** (bNumEndpoints = 0)
- Verwijst naar Interface 1 (MIDI Streaming)

### 3.2 MIDI Streaming Interface

```c
// Standard Interface Descriptor
0x09,                     // bLength: 9 bytes
0x04,                     // bDescriptorType: INTERFACE
0x01,                     // bInterfaceNumber: 1
0x00,                     // bAlternateSetting: 0
0x02,                     // bNumEndpoints: 2 (Bulk IN + Bulk OUT)
0x01,                     // bInterfaceClass: AUDIO (0x01)
0x03,                     // bInterfaceSubClass: MIDISTREAMING (0x03)
0x00,                     // bInterfaceProtocol: 0
0x00,                     // iInterface: 0

// Class-Specific MS Interface Header
0x07,                     // bLength: 7 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x01,                     // bDescriptorSubtype: MS_HEADER
0x00, 0x01,               // bcdMSC: MIDI Streaming Class v1.0
0x41, 0x00,               // wTotalLength: 65 bytes (header + jacks)
```

**Belangrijkste**:
- **bInterfaceSubClass = 0x03**: Dit maakt het een MIDI device!
- **bNumEndpoints = 2**: Bulk IN en Bulk OUT
- **wTotalLength = 65**: Lengte van MS header + alle jack descriptors

---

## 4. MIDI Jack Descriptors

MIDI Jacks definiëren de logische MIDI inputs en outputs.

### MIDI Jack Types:
- **Embedded (0x01)**: Virtuele MIDI jack (USB)
- **External (0x02)**: Fysieke MIDI jack (5-pin DIN)

Voor pure USB MIDI zonder fysieke MIDI connectors gebruiken we alleen Embedded jacks.

### Standard MIDI Jack Configuratie:

```
HOST
  ↓ USB OUT Endpoint
[MIDI IN Jack (Embedded) - ID:1] ← Ontvangt van host
  ↓
[MIDI OUT Jack (External) - ID:4] → "Naar externe device" (logisch)


HOST
  ↑ USB IN Endpoint
[MIDI OUT Jack (Embedded) - ID:3] ← Stuurt naar host
  ↑
[MIDI IN Jack (External) - ID:2] ← "Van extern device" (logisch)
```

### MIDI IN Jack (Embedded) - ID 1

```c
0x06,                     // bLength: 6 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x02,                     // bDescriptorSubtype: MIDI_IN_JACK
0x01,                     // bJackType: EMBEDDED
0x01,                     // bJackID: 1
0x00,                     // iJack: 0
```

### MIDI IN Jack (External) - ID 2

```c
0x06,                     // bLength: 6 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x02,                     // bDescriptorSubtype: MIDI_IN_JACK
0x02,                     // bJackType: EXTERNAL
0x02,                     // bJackID: 2
0x00,                     // iJack: 0
```

### MIDI OUT Jack (Embedded) - ID 3

```c
0x09,                     // bLength: 9 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x03,                     // bDescriptorSubtype: MIDI_OUT_JACK
0x01,                     // bJackType: EMBEDDED
0x03,                     // bJackID: 3
0x01,                     // bNrInputPins: 1
0x02,                     // baSourceID(1): External Jack 2
0x01,                     // baSourcePin(1): Pin 1
0x00,                     // iJack: 0
```

**Routing**: External IN Jack (2) → Embedded OUT Jack (3) → Host

### MIDI OUT Jack (External) - ID 4

```c
0x09,                     // bLength: 9 bytes
0x24,                     // bDescriptorType: CS_INTERFACE
0x03,                     // bDescriptorSubtype: MIDI_OUT_JACK
0x02,                     // bJackType: EXTERNAL
0x04,                     // bJackID: 4
0x01,                     // bNrInputPins: 1
0x01,                     // baSourceID(1): Embedded Jack 1
0x01,                     // baSourcePin(1): Pin 1
0x00,                     // iJack: 0
```

**Routing**: Host → Embedded IN Jack (1) → External OUT Jack (4)

---

## 5. Endpoint Descriptors

USB MIDI gebruikt **Bulk endpoints** voor data transfer.

### Bulk OUT Endpoint (Host → Device)

```c
// Standard Endpoint Descriptor
0x09,                     // bLength: 9 bytes
0x05,                     // bDescriptorType: ENDPOINT
0x01,                     // bEndpointAddress: OUT Endpoint 1
0x02,                     // bmAttributes: Bulk transfer
0x40, 0x00,               // wMaxPacketSize: 64 bytes
0x00,                     // bInterval: 0 (ignored for Bulk)
0x00,                     // bRefresh: 0
0x00,                     // bSynchAddress: 0

// Class-Specific MS Bulk OUT Endpoint Descriptor
0x05,                     // bLength: 5 bytes
0x25,                     // bDescriptorType: CS_ENDPOINT
0x01,                     // bDescriptorSubtype: MS_GENERAL
0x01,                     // bNumEmbMIDIJack: 1
0x01,                     // baAssocJackID(1): Embedded Jack 1
```

### Bulk IN Endpoint (Device → Host)

```c
// Standard Endpoint Descriptor
0x09,                     // bLength: 9 bytes
0x05,                     // bDescriptorType: ENDPOINT
0x81,                     // bEndpointAddress: IN Endpoint 1
0x02,                     // bmAttributes: Bulk transfer
0x40, 0x00,               // wMaxPacketSize: 64 bytes
0x00,                     // bInterval: 0 (ignored for Bulk)
0x00,                     // bRefresh: 0
0x00,                     // bSynchAddress: 0

// Class-Specific MS Bulk IN Endpoint Descriptor
0x05,                     // bLength: 5 bytes
0x25,                     // bDescriptorType: CS_ENDPOINT
0x01,                     // bDescriptorSubtype: MS_GENERAL
0x01,                     // bNumEmbMIDIJack: 1
0x03,                     // baAssocJackID(1): Embedded Jack 3
```

**Belangrijke punten**:
- **bmAttributes = 0x02**: Bulk transfer (beste voor MIDI)
- **wMaxPacketSize = 64**: Maximum 64 bytes per transfer
- **bEndpointAddress**:
  - Bit 7: Direction (0 = OUT, 1 = IN)
  - Bits 0-3: Endpoint number (1)
  - OUT = 0x01, IN = 0x81

---

## USB MIDI Data Format

### USB MIDI Packet (4 bytes)

```
Byte 0: [Cable Number 4 bits][Code Index Number 4 bits]
Byte 1: MIDI Status Byte
Byte 2: MIDI Data Byte 1
Byte 3: MIDI Data Byte 2
```

### Code Index Number (CIN)

| CIN | Message Type |
|-----|--------------|
| 0x8 | Note OFF |
| 0x9 | Note ON |
| 0xA | Poly Key Pressure |
| 0xB | Control Change |
| 0xC | Program Change |
| 0xD | Channel Pressure |
| 0xE | Pitch Bend |
| 0xF | Single Byte |

### Voorbeeld: Note ON

```
MIDI Message: 0x90 0x3C 0x7F
USB Packet:   0x09 0x90 0x3C 0x7F

Uitleg:
- 0x09: Cable 0, CIN = Note ON
- 0x90: Channel 1, Note ON
- 0x3C: Note 60 (Middle C)
- 0x7F: Velocity 127
```

---

## Totale Descriptor Size Berekening

```
Device Descriptor:                    18 bytes
Configuration Descriptor:              9 bytes
AC Interface Descriptor:               9 bytes
AC Class-Specific Header:              9 bytes
MS Interface Descriptor:               9 bytes
MS Class-Specific Header:              7 bytes
MIDI IN Jack (Embedded):               6 bytes
MIDI IN Jack (External):               6 bytes
MIDI OUT Jack (Embedded):              9 bytes
MIDI OUT Jack (External):              9 bytes
Bulk OUT Endpoint:                     9 bytes
CS Bulk OUT Endpoint:                  5 bytes
Bulk IN Endpoint:                      9 bytes
CS Bulk IN Endpoint:                   5 bytes
                                    ─────────
TOTAL:                               119 bytes

Configuration wTotalLength:          101 bytes
(excludes Device Descriptor)
```

---

## Verificatie Tools

### Windows: USBTreeView
- Download: https://www.uwe-sieber.de/usbtreeview_e.html
- Toont volledige descriptor tree
- Controleer of alle descriptors correct zijn

### Linux: lsusb
```bash
lsusb -v -d 0483:5740
```

### MIDI-View
- Verifieert of MIDI messages correct geïnterpreteerd worden

---

## Common Mistakes

❌ **Fout**: bDeviceClass = 0x01 in Device Descriptor
✅ **Correct**: bDeviceClass = 0x00 (class defined in interface)

❌ **Fout**: wTotalLength vergeten bij te werken
✅ **Correct**: Tel alle bytes vanaf Configuration Descriptor

❌ **Fout**: Endpoint adres 0x01 voor IN endpoint
✅ **Correct**: Endpoint adres 0x81 (bit 7 = IN)

❌ **Fout**: MIDI Jack IDs niet consistent
✅ **Correct**: Unieke IDs en correcte source ID referenties

---

## Referenties

- **USB MIDI Class Specification v1.0**:  
  https://www.usb.org/sites/default/files/midi10.pdf

- **USB 2.0 Specification**:  
  https://www.usb.org/document-library/usb-20-specification

- **USB Audio Device Class v1.0**:  
  https://www.usb.org/document-library/audio-device-document-10
