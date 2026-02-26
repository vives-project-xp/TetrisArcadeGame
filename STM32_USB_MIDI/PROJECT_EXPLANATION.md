# Project Overzicht & Uitleg

## Wat heb je gemaakt?

Je hebt de STM32H533RE Nucleo-board geconfigureerd als een **USB MIDI Class Device**. Dit betekent dat je microcontroller nu kan communiceren met MIDI software op je computer via USB, zonder dat er speciale drivers nodig zijn.

## Hoe werkt het?

### High-Level Architectuur

```
┌──────────────────────┐
│   COMPUTER (HOST)    │
│                      │
│  ┌────────────────┐ │
│  │  MIDI Software │ │  (MIDI-View, DAW, etc.)
│  │   (MIDI-View)  │ │
│  └────────┬───────┘ │
│           │         │
│  ┌────────▼───────┐ │
│  │  USB MIDI      │ │
│  │  Driver (OS)   │ │
│  └────────┬───────┘ │
└───────────┼─────────┘
            │ USB Cable
┌───────────▼─────────┐
│  NUCLEO-H533RE      │
│                     │
│  ┌────────────────┐ │
│  │ USB Hardware   │ │  PA11/PA12 (USB D-/D+)
│  │ (PHY)          │ │
│  └────────┬───────┘ │
│           │         │
│  ┌────────▼───────┐ │
│  │ USB Device     │ │
│  │ Middleware     │ │
│  │ (HAL Library)  │ │
│  └────────┬───────┘ │
│           │         │
│  ┌────────▼───────┐ │
│  │ USB MIDI Class │ │  usbd_midi.c/h
│  │ Implementation │ │
│  └────────┬───────┘ │
│           │         │
│  ┌────────▼───────┐ │
│  │ Application    │ │  main.c
│  │ (Button→MIDI)  │ │
│  └────────────────┘ │
│                     │
│  [Button] [LED]     │
│    PC13     PA5     │
└─────────────────────┘
```

### Data Flow: Button Press → MIDI Note ON

```
1. USER DRUK OP BUTTON
   └─→ PC13 GPIO pin gaat LOW

2. MAIN.C DETECTEERT BUTTON
   └─→ Debounce logic (50ms)
   └─→ State change: pressed

3. APPLICATIE ROEPT AAN:
   └─→ USBD_MIDI_SendNoteOn(...)

4. USB MIDI CLASS CONSTRUEERT PACKET
   └─→ 4 bytes: [0x09][0x90][0x3C][0x7F]
              CIN   Status Note Velocity

5. USB DEVICE MIDDLEWARE TRANSMIT
   └─→ USBD_LL_Transmit(EP1_IN, data, 4)

6. USB HARDWARE (PHY)
   └─→ D+/D- physical signaling

7. COMPUTER USB ONTVANGT
   └─→ OS USB Stack
   └─→ USB MIDI Driver
   └─→ MIDI Software (MIDI-View)
   └─→ DISPLAY: "Note ON, Chan 1, Note 60"
```

---

## Code Uitleg: Belangrijkste Componenten

### 1. main.c - Application Layer

**Responsibilities**:
- System clock configuration
- GPIO initialization (Button, LED)
- USB Device initialization
- Main loop: button polling & MIDI send

**Key Code**:
```c
// Button state machine
uint8_t button_state = 1;          // Current debounced state
uint8_t last_button_state = 1;     // Previous reading
uint32_t last_debounce_time = 0;   // Timestamp for debouncing

// In main loop:
uint8_t reading = HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN);

if (reading != last_button_state) {
  last_debounce_time = HAL_GetTick();  // Reset timer
}

if ((HAL_GetTick() - last_debounce_time) > debounce_delay) {
  if (reading != button_state) {
    button_state = reading;
    
    if (button_state == 0) {  // Pressed (active LOW)
      USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MAX);
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
    } else {  // Released
      USBD_MIDI_SendNoteOff(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MED);
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
    }
  }
}
```

**Waarom debouncing?**
Mechanical buttons "bounce" - ze maken/breken het contact meerdere keren bij press/release. Debouncing filtert dit door pas een state change te accepteren na een stabiele periode (50ms).

---

### 2. usbd_midi.c - USB MIDI Class Implementation

**Responsibilities**:
- USB MIDI Descriptor definitie
- USB Class callbacks (Init, DeInit, Setup, DataIn, DataOut)
- MIDI message packetization
- Helper functions voor Note ON/OFF/CC

**Key Components**:

#### A. USB Descriptor
```c
__ALIGN_BEGIN static uint8_t USBD_MIDI_CfgDesc[101] __ALIGN_END =
{
  // Configuration Descriptor (9 bytes)
  0x09, 0x02, 0x65, 0x00, 0x02, 0x01, 0x00, 0xC0, 0x32,
  
  // Audio Control Interface (18 bytes)
  // - Standard Interface Descriptor (9 bytes)
  // - Class-Specific AC Header (9 bytes)
  
  // MIDI Streaming Interface (74 bytes)
  // - Standard Interface Descriptor (9 bytes)
  // - Class-Specific MS Header (7 bytes)
  // - MIDI IN Jack Embedded (6 bytes)
  // - MIDI IN Jack External (6 bytes)
  // - MIDI OUT Jack Embedded (9 bytes)
  // - MIDI OUT Jack External (9 bytes)
  // - Bulk OUT Endpoint + CS (9+5 bytes)
  // - Bulk IN Endpoint + CS (9+5 bytes)
};
```

**Waarom deze structuur?**
USB MIDI is een subclass van USB Audio Class. Daarom is een Audio Control Interface verplicht (ook al doet die niets). De MIDI Streaming Interface bevat de daadwerkelijke MIDI functionaliteit.

#### B. Class Callbacks
```c
USBD_ClassTypeDef USBD_MIDI =
{
  USBD_MIDI_Init,        // Geroepen bij USB enumeration
  USBD_MIDI_DeInit,      // Geroepen bij disconnect
  USBD_MIDI_Setup,       // Geroepen voor control requests
  NULL,                  // EP0_TxSent
  USBD_MIDI_EP0_RxReady,
  USBD_MIDI_DataIn,      // Geroepen na succesvolle transmit
  USBD_MIDI_DataOut,     // Geroepen bij ontvangen data
  // ... other callbacks
};
```

**Init Callback**:
```c
static uint8_t USBD_MIDI_Init(USBD_HandleTypeDef *pdev, uint8_t cfgidx)
{
  // Allocate memory voor class data
  hmidi = USBD_malloc(sizeof(USBD_MIDI_HandleTypeDef));
  
  // Open Bulk IN endpoint (Device → Host)
  USBD_LL_OpenEP(pdev, MIDI_IN_EP, USBD_EP_TYPE_BULK, 64);
  
  // Open Bulk OUT endpoint (Host → Device)
  USBD_LL_OpenEP(pdev, MIDI_OUT_EP, USBD_EP_TYPE_BULK, 64);
  
  // Prepare to receive data
  USBD_LL_PrepareReceive(pdev, MIDI_OUT_EP, hmidi->rx_buffer, 64);
  
  return USBD_OK;
}
```

#### C. Note ON Helper Function
```c
uint8_t USBD_MIDI_SendNoteOn(USBD_HandleTypeDef *pdev, 
                              uint8_t channel, 
                              uint8_t note, 
                              uint8_t velocity)
{
  uint8_t midi_packet[4];
  
  // Byte 0: Cable Number (0) + Code Index Number (0x9 = Note ON)
  midi_packet[0] = (MIDI_CIN_NOTE_ON << 4) | (channel & 0x0F);
  
  // Byte 1: MIDI Status Byte (0x90 = Note ON Channel 1)
  midi_packet[1] = MIDI_STATUS_NOTE_ON | (channel & 0x0F);
  
  // Byte 2: Note Number (0-127)
  midi_packet[2] = note & 0x7F;
  
  // Byte 3: Velocity (0-127)
  midi_packet[3] = velocity & 0x7F;
  
  return USBD_MIDI_SendData(pdev, midi_packet, 4);
}
```

**Packet Format Uitleg**:
```
USB MIDI Packet (4 bytes):

Byte 0: [Cable Number: 4 bits][Code Index Number: 4 bits]
        └─ Cable 0 (single virtual MIDI port)
        └─ CIN 0x9 (Note ON indicator for USB layer)

Byte 1: [Status: 4 bits][Channel: 4 bits]
        └─ 0x9 = Note ON
        └─ Channel 0-15 (MIDI channels 1-16)

Byte 2: Note Number (0-127)
        └─ 60 = Middle C (C4)

Byte 3: Velocity (0-127)
        └─ 127 = Maximum velocity (hardest hit)
```

---

### 3. usbd_desc.c - USB Device Descriptors

**Responsibilities**:
- Device Descriptor (VID, PID, versie info)
- String Descriptors (manufacturer, product, serial)
- Device Qualifier Descriptor

**Device Descriptor**:
```c
__ALIGN_BEGIN uint8_t USBD_FS_DeviceDesc[18] __ALIGN_END =
{
  0x12,                       // bLength: 18 bytes
  USB_DESC_TYPE_DEVICE,       // bDescriptorType: Device
  0x00, 0x02,                 // bcdUSB: USB 2.0
  0x00,                       // bDeviceClass: Defined in Interface
  0x00,                       // bDeviceSubClass
  0x00,                       // bDeviceProtocol
  USB_MAX_EP0_SIZE,           // bMaxPacketSize0: 64 bytes
  LOBYTE(0x0483),             // idVendor: STMicroelectronics
  HIBYTE(0x0483),
  LOBYTE(0x5740),             // idProduct: Custom MIDI
  HIBYTE(0x5740),
  0x00, 0x02,                 // bcdDevice: Release 2.00
  USBD_IDX_MFC_STR,           // iManufacturer: String index 1
  USBD_IDX_PRODUCT_STR,       // iProduct: String index 2
  USBD_IDX_SERIAL_STR,        // iSerialNumber: String index 3
  USBD_MAX_NUM_CONFIGURATION  // bNumConfigurations: 1
};
```

**Serial Number Generation**:
```c
// Uses unique device ID from MCU
deviceserial0 = *(uint32_t *)DEVICE_ID1;  // 0x1FF1E800
deviceserial1 = *(uint32_t *)DEVICE_ID2;  // 0x1FF1E804
deviceserial2 = *(uint32_t *)DEVICE_ID3;  // 0x1FF1E808

// Converts to hex string (e.g., "1234ABCD5678EF90")
```

**Waarom unique serial?**
Elk STM32 heeft een unieke 96-bit ID. Door deze te gebruiken als serial number kan de OS meerdere identieke devices onderscheiden.

---

## USB MIDI Protocol Deep Dive

### USB vs "Classic" MIDI

| Aspect | Classic MIDI (DIN-5) | USB MIDI |
|--------|---------------------|----------|
| **Physical** | 5-pin DIN connector | USB connector |
| **Speed** | 31.25 kbaud (~3 KB/s) | 12 Mbps (Full-Speed) |
| **Protocol** | Serial UART | USB Bulk Transfer |
| **Packet** | 3 bytes raw | 4 bytes (USB wrapped) |
| **Cable** | Max 15m | Max 5m (passive) |
| **Power** | Separate | Bus-powered (5V) |

**USB MIDI wraps classic MIDI**:
```
Classic MIDI: [Status][Data1][Data2]
              [0x90]  [0x3C] [0x7F]

USB MIDI:     [CIN/Cable][Status][Data1][Data2]
              [0x09]     [0x90]  [0x3C] [0x7F]
              └─ Extra byte voor USB routing
```

### Code Index Number (CIN)

CIN helpt USB host om MIDI messages te interpreteren zonder status byte te parsen:

| CIN | Type | MIDI Status | Bytes |
|-----|------|-------------|-------|
| 0x8 | Note OFF | 0x80-0x8F | 3 |
| 0x9 | Note ON | 0x90-0x9F | 3 |
| 0xA | Poly Key Pressure | 0xA0-0xAF | 3 |
| 0xB | Control Change | 0xB0-0xBF | 3 |
| 0xC | Program Change | 0xC0-0xCF | 2 |
| 0xD | Channel Pressure | 0xD0-0xDF | 2 |
| 0xE | Pitch Bend | 0xE0-0xEF | 3 |
| 0xF | System Message | 0xF0-0xFF | 1-3 |

**Waarom CIN?**
USB Bulk transfers hebben geen frame structure. CIN laat host weten hoeveel bytes geldig zijn in het 4-byte packet (sommige messages zijn maar 2 bytes).

---

## Clock Configuration Uitleg

### Waarom exact 48 MHz voor USB?

USB Full-Speed vereist exact **48.000 MHz** ±0.25% voor bit timing.

**Opties**:

#### Optie 1: HSI48 (Gebruikt in ons project)
```
HSI48 (Internal RC Oscillator)
└─→ 48 MHz ±1% direct naar USB

Voordelen:
✅ Simpel (geen PLL configuratie)
✅ USB-specifieke oscillator
✅ Clock Recovery System (CRS) voor nauwkeurigheid

Nadelen:
❌ Minder accuraat dan crystal
❌ Kan alleen voor USB gebruikt worden
```

#### Optie 2: PLL van HSE
```
HSE 8 MHz (External Crystal)
└─→ PLL: /M=1, ×N=96, /Q=2
└─→ 48 MHz (exact) naar USB

Voordelen:
✅ Zeer accuraat (crystal-based)
✅ PLL kan ook SYSCLK genereren

Nadelen:
❌ Complexere configuratie
❌ Vereist externe crystal
```

### Volledige Clock Tree (ons project)

```
┌─ External ──────────────┐
│ HSE: 8 MHz (ST-Link MCO)│
└─────┬───────────────────┘
      │
      ▼
┌─ PLL1 ──────────────┐
│ /M: 2  → 4 MHz VCO  │
│ ×N: 125  → 500 MHz  │
│ /P: 2  → 250 MHz    │────→ SYSCLK (CPU, AHB, APB)
└─────────────────────┘

┌─ Internal ─────────────┐
│ HSI48: 48 MHz (±1%)    │────→ USB Clock
└────────────────────────┘

Result:
- CPU: 250 MHz (max for H533RE)
- USB: 48 MHz (required)
- Peripherals: 250 MHz
```

**Verificatie in code**:
```c
// SystemClock_Config() in main.c
RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;  // Enable HSI48

// USB Clock source
PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;
```

---

## Memory Layout

### STM32H533RE Memory Map

```
0x0800 0000 ┌──────────────────────┐
            │ FLASH (512 KB)       │
            │ - Code               │
            │ - Constants          │
            │ - USB Descriptors    │
0x0807 FFFF └──────────────────────┘

0x2000 0000 ┌──────────────────────┐
            │ SRAM1 (64 KB)        │
            │ - Stack              │
            │ - Heap               │
            │ - Variables          │
            │ - USB buffers        │
0x2000 FFFF └──────────────────────┘

0x2001 0000 ┌──────────────────────┐
            │ SRAM2 (192 KB)       │
0x2003 FFFF └──────────────────────┘

0x4000 0000 ┌──────────────────────┐
            │ Peripherals          │
            │ - USB registers      │
            │ - GPIO               │
            │ - Timers, etc.       │
0x5FFF FFFF └──────────────────────┘
```

### USB Buffers

```c
// In USBD_MIDI_HandleTypeDef
typedef struct
{
  uint8_t  tx_buffer[64];  // Transmit buffer (IN endpoint)
  uint8_t  rx_buffer[64];  // Receive buffer (OUT endpoint)
  // ... other state ...
} USBD_MIDI_HandleTypeDef;
```

**Allocated dynamically tijdens Init**:
```c
hmidi = USBD_malloc(sizeof(USBD_MIDI_HandleTypeDef));
// Allocated on heap, ~140 bytes total
```

---

## Waarom deze libraries?

### STM32 USB Device Middleware

**Voordelen**:
- ✅ Officiële ST library (goed ondersteund)
- ✅ Hardware Abstraction Layer (HAL) compatible
- ✅ Werkt met STM32CubeMX code generator
- ✅ Proven in production (ST gebruikt het zelf)
- ✅ Goede documentatie

**Alternatieven**:

1. **TinyUSB**:
   - Modern, cross-platform USB stack
   - Maar: Vereist meer manual setup, geen CubeMX integration

2. **libusb_stm32**:
   - Lightweight, bare-metal USB library
   - Maar: Minder features, geen HAL integration

3. **Custom Implementation**:
   - Volledig van scratch USB protocol implementeren
   - Maar: Months of work, error-prone, not recommended

**Conclusie**: Voor educational purposes en snelle development is STM32 HAL + Custom MIDI class de beste keuze.

---

## Wat je geleerd hebt

### USB Concepten
- ✅ USB Device vs Host
- ✅ USB Enumeration process
- ✅ Descriptors (Device, Configuration, Interface, Endpoint)
- ✅ Bulk transfers vs Interrupt/Isochronous
- ✅ Endpoint directions (IN/OUT relative to host)

### MIDI Protocol
- ✅ MIDI messages (Note ON/OFF, Control Change, etc.)
- ✅ Status bytes, data bytes
- ✅ Channels (1-16)
- ✅ USB MIDI packetization (CIN + 3 MIDI bytes)

### Embedded Systems
- ✅ GPIO (button input, LED output)
- ✅ Debouncing techniques
- ✅ Clock configuration (PLL, HSI48)
- ✅ Interrupt-driven vs polled I/O
- ✅ State machines

### STM32 Ecosystem
- ✅ STM32CubeMX configuration tool
- ✅ HAL (Hardware Abstraction Layer)
- ✅ USB Device Middleware
- ✅ Building custom USB device classes

---

## Comparison: Voor/Na

### Voor (Zonder USB MIDI)

```c
// Classic UART MIDI (requires MIDI shield)
void sendMIDI(uint8_t status, uint8_t data1, uint8_t data2) {
  HAL_UART_Transmit(&huart1, &status, 1, 100);
  HAL_UART_Transmit(&huart1, &data1, 1, 100);
  HAL_UART_Transmit(&huart1, &data2, 1, 100);
}
// 31.25 kbaud, requires MIDI-to-USB adapter, extra hardware
```

### Na (Met USB MIDI)

```c
// Direct USB MIDI
USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, 60, 127);
// 12 Mbps, plug-and-play, no adapters needed
```

**Benefits**:
- 🚀 384x faster (12 Mbps vs 31.25 kbaud)
- 💰 No extra hardware (no MIDI shield, no USB adapter)
- 🔌 Plug-and-play (OS recognizes USB MIDI device)
- ⚡ Bus-powered (no external power supply)

---

## Future Improvements

### 1. MIDI IN (Receive from Host)

Currently: Device → Host only (Note ON/OFF)

Add in `USBD_MIDI_DataOut`:
```c
static uint8_t USBD_MIDI_DataOut(USBD_HandleTypeDef *pdev, uint8_t epnum)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDEF *)pdev->pClassData;

  // Get received data
  uint32_t length = USBD_LL_GetRxDataSize(pdev, epnum);
  
  // Parse MIDI packets
  for (uint32_t i = 0; i < length; i += 4) {
    uint8_t cin = hmidi->rx_buffer[i] >> 4;
    uint8_t status = hmidi->rx_buffer[i+1];
    uint8_t data1 = hmidi->rx_buffer[i+2];
    uint8_t data2 = hmidi->rx_buffer[i+3];
    
    // Process: e.g., control LED with Note ON/OFF from host
    if (cin == MIDI_CIN_NOTE_ON && status == 0x90) {
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
    } else if (cin == MIDI_CIN_NOTE_OFF && status == 0x80) {
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
    }
  }
  
  // Prepare for next reception
  USBD_LL_PrepareReceive(pdev, MIDI_OUT_EP, hmidi->rx_buffer, 64);
  
  return USBD_OK;
}
```

### 2. Multiple Virtual Cables

USB MIDI supports 16 virtual "cables" (ports):
```c
// Cable 0: Synth notes
USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, 60, 127, 0);  // cable 0
                                                      //        ^

// Cable 1: Drum machine
USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 9, 36, 127, 1);  // cable 1
                                                      //        ^
```

### 3. SysEx Messages

System Exclusive for device configuration:
```c
uint8_t sysex[] = {
  0xF0,  // SysEx start
  0x7D,  // Manufacturer ID (non-commercial)
  0x01, 0x02, 0x03,  // Your data
  0xF7   // SysEx end
};
USBD_MIDI_SendSysEx(&hUsbDeviceFS, sysex, sizeof(sysex));
```

### 4. ADC Velocity Sensing

```c
// Read ADC for velocity
HAL_ADC_Start(&hadc1);
HAL_ADC_PollForConversion(&hadc1, 100);
uint16_t adc_value = HAL_ADC_GetValue(&hadc1);

// Convert to MIDI velocity (0-127)
uint8_t velocity = (adc_value * 127) / 4095;

USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, note, velocity);
```

---

## Resources & References

### Official Documentation
- [USB MIDI Class Specification v1.0](https://www.usb.org/sites/default/files/midi10.pdf)
- [STM32H533RE Datasheet](https://www.st.com/resource/en/datasheet/stm32h533re.pdf)
- [Nucleo-H533RE User Manual (UM3186)](https://www.st.com/resource/en/user_manual/um3186-stm32h5-nucleo64-board-mb1813-stmicroelectronics.pdf)

### Tools
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)
- [MIDI-View](http://hautetechnique.com/midi/midiview/)
- [USBTreeView](https://www.uwe-sieber.de/usbtreeview_e.html) - USB descriptor viewer

### Learning
- [MIDI Association](https://www.midi.org/) - Official MIDI specs
- [USB in a NutShell](https://www.beyondlogic.org/usbnutshell/usb1.shtml) - USB tutorial
- [ST Training Materials](https://www.st.com/content/st_com/en/support/learning/stm32-education.html)

---

## Conclusie

Je hebt nu:
- ✅ Een werkende USB MIDI device
- ✅ Begrip van USB protocol (descriptors, endpoints, enumeration)
- ✅ Kennis van MIDI protocol (messages, channels, packetization)
- ✅ Ervaring met STM32 HAL en middleware
- ✅ Troubleshooting skills (hardware + software debugging)

**Dit project is de basis voor**:
- 🎹 Custom MIDI controllers (keyboards, drum pads)
- 🎛️ DJ controllers (faders, knobs, buttons)
- 🎵 Sequencers en arpeggiators
- 🔊 Audio synthesizers met MIDI control
- 🎮 Game controllers (as USB HID device - similar concepts)

**Next steps**: Experimenteer, breidt uit, en belangrijkst: have fun! 🎉
