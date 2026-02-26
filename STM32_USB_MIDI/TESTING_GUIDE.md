# Testing & Verification Guide

## Software Tools Installatie

### 1. MIDI-View (Aanbevolen voor Windows)

**Download**:
- Website: http://hautetechnique.com/midi/midiview/
- Direct link: Download MIDI-View installer

**Installatie**:
1. Run `MIDIView_Setup.exe`
2. Volg de installatie wizard
3. Geen speciale drivers nodig

**Alternatief: MIDI-OX**
- Download: http://www.midiox.com/
- Meer geavanceerde features
- Grotere learning curve

---

## Device Herkenning Verificatie

### Stap 1: Windows Device Manager Check

1. **Open Device Manager**:
   - Windows + X → Device Manager
   - Of: Win + R → `devmgmt.msc`

2. **Zoek het device**:
   ```
   📂 Sound, video and game controllers
      └─ 🔊 USB Audio Device
   ```
   
   Of:
   ```
   📂 Universal Serial Bus devices
      └─ 🔌 STM32 MIDI Device
   ```

3. **Controleer Properties**:
   - Right-click → Properties
   - Details tab → Hardware Ids
   - Zou moeten tonen:
     ```
     USB\VID_0483&PID_5740&REV_0200
     USB\VID_0483&PID_5740
     ```

### Screenshot 1: Device Manager ✅ VEREIST

**Wat te capturen**:
- Device Manager window
- "Sound, video and game controllers" expanded
- "USB Audio Device" of "STM32 MIDI Device" zichtbaar
- (Optioneel) Properties window met Hardware Ids

**Voorbeeld layout**:
```
┌─ Device Manager ────────────────────────────┐
│ ⊞ Sound, video and game controllers         │
│   ├─ 🔊 High Definition Audio Device        │
│   └─ 🔊 USB Audio Device ◄── DIT!          │
│                                              │
│ Properties: USB Audio Device ───────────┐  │
│ │ General | Driver | Details | Events │  │  │
│ │                                       │  │  │
│ │ Hardware Ids:                        │  │  │
│ │ USB\VID_0483&PID_5740&REV_0200      │  │  │
│ │ USB\VID_0483&PID_5740               │  │  │
│ └───────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## MIDI Functionaliteit Test

### Stap 2: MIDI-View Configuratie

1. **Open MIDI-View**
2. **Configure MIDI Inputs**:
   - Menu: Options → MIDI Devices
   - Input lijst zou moeten tonen:
     ```
     ☐ Microsoft GS Wavetable Synth
     ☑ STM32 MIDI Device        ◄── Vink aan!
     ```
3. **Filter Settings** (optioneel):
   - Menu: View → Filters
   - Enable All (om alle messages te zien)

### Screenshot 2: MIDI-View Device Selection ✅ VEREIST

**Wat te capturen**:
- MIDI Devices dialog
- STM32 MIDI Device in de lijst
- Checkbox aangevinkt

### Stap 3: Test Note ON/OFF Messages

1. **Druk op User Button** (blauw, PC13) op Nucleo board
2. **Observe MIDI-View main window**

**Verwachte output**:
```
Time        Status  Chan  Data1  Data2   Event
──────────────────────────────────────────────────
12:34:56.123  90     1     60     127    Note On
12:34:56.456  80     1     60     64     Note Off
```

**Uitleg**:
- **90**: Note ON status (0x90)
- **80**: Note OFF status (0x80)
- **Chan 1**: MIDI Channel 1
- **Data1 (60)**: Note number (Middle C)
- **Data2 (ON:127, OFF:64)**: Velocity

### Screenshot 3: MIDI Messages ✅ VEREIST

**Wat te capturen**:
- MIDI-View main window
- Lijst met Note ON en Note OFF events
- Timestamp, status, channel, en data zichtbaar
- **Highlight** de Note ON en Note OFF regels

**Voorbeeld layout**:
```
┌─ MIDI-View ─────────────────────────────────────────┐
│ Input: STM32 MIDI Device                            │
├─────────────────────────────────────────────────────┤
│ Time          Status  Ch  D1   D2    Event         │
│ ─────────────────────────────────────────────────  │
│ 14:23:45.123   90     1   60   127   Note On  ◄─┐ │
│ 14:23:45.456   80     1   60   64    Note Off ◄─┤ │
│ 14:23:47.789   90     1   60   127   Note On  ◄─│ │
│ 14:23:48.012   80     1   60   64    Note Off ◄─┘ │
│                                      DEZE TONEN!   │
└─────────────────────────────────────────────────────┘
```

---

## Uitgebreide Tests

### Test 1: Multiple Note Events

**Procedure**:
1. Druk User Button 5x snel
2. Verwacht: 5 Note ON + 5 Note OFF pairs

**Verificatie**:
- Alle events in chronologische volgorde
- Consistent velocity values
- Correct channel (1)

### Test 2: LED Feedback

**Procedure**:
1. Druk User Button
2. Observeer groene LED (PA5)

**Verwacht gedrag**:
- LED ON wanneer Note ON verstuurd
- LED OFF wanneer Note OFF verstuurd
- Synchronisatie met MIDI events

### Test 3: USB Reconnect

**Procedure**:
1. Disconnect USB kabel
2. Sluit opnieuw aan
3. Check Device Manager
4. Test opnieuw met MIDI-View

**Verwacht**:
- Device re-enumeration succesvol
- MIDI messages weer ontvangen

---

## Advanced: Raw USB Data Analyse

### Tool: Wireshark met USBPcap

1. **Install USBPcap**: https://desowin.org/usbpcap/
2. **Install Wireshark**: https://www.wireshark.org/
3. **Capture USB traffic**:
   - Select USBPcap interface
   - Apply filter: `usb.idVendor == 0x0483 && usb.idProduct == 0x5740`

### Verificatie: USB MIDI Packet

**Expected raw data voor Note ON**:
```
09 90 3C 7F
│  │  │  └─ Velocity (127)
│  │  └──── Note (60 = 0x3C)
│  └─────── Status (Note ON Ch1)
└────────── CIN (0x9) + Cable (0)
```

**Screenshot 4 (OPTIONEEL): Wireshark Capture**
- USB traffic met MIDI packets
- Hex dump showing `09 90 3C 7F`

---

## Alternatieve Test Platforms

### Linux

**lsusb verificatie**:
```bash
lsusb
# Output: Bus 001 Device 005: ID 0483:5740 STMicroelectronics

lsusb -v -d 0483:5740
# Shows full descriptor tree
```

**ALSA MIDI check**:
```bash
aconnect -l
# Output:
# client 20: 'STM32 MIDI Device' [type=kernel]
#     0 'STM32 MIDI Device MIDI 1'
```

**Test met amidi**:
```bash
amidi -l
amidi -p hw:2,0 -d
# Press User Button, should see hex MIDI data
```

### macOS

**Audio MIDI Setup**:
1. Open `/Applications/Utilities/Audio MIDI Setup.app`
2. Window → Show MIDI Studio
3. "STM32 MIDI Device" should appear

**Test with MIDI Monitor**:
- Download: https://www.snoize.com/MIDIMonitor/
- Similar functionality to MIDI-View

---

## Screenshot Checklist voor Deliverable

Voor de opdracht heb je nodig:

### ✅ Screenshot 1: Device Manager
- [ ] Device Manager geopend
- [ ] "Sound, video and game controllers" zichtbaar
- [ ] "USB Audio Device" of "STM32 MIDI Device" in lijst
- [ ] (Optioneel) Properties met VID/PID

### ✅ Screenshot 2: MIDI-View Device Selection  
- [ ] MIDI-View Options → MIDI Devices
- [ ] "STM32 MIDI Device" in input lijst
- [ ] Checkbox aangevinkt

### ✅ Screenshot 3: MIDI Messages
- [ ] MIDI-View main window
- [ ] Tenminste 2 Note ON events
- [ ] Tenminste 2 Note OFF events
- [ ] Timestamps zichtbaar
- [ ] Correct channel (1) en note (60)

### Extra (Nice to have):
- [ ] Video van button press → LED → MIDI message
- [ ] Wireshark USB capture
- [ ] Device descriptor dump (USBTreeView)

---

## Wat te doen bij geen MIDI Messages?

### Checklist:

1. **Device herkend in Device Manager?**
   - ❌ Nee → Zie "Device Recognition Problems"
   - ✅ Ja → Ga verder

2. **MIDI-View ziet device?**
   - ❌ Nee → Herstart MIDI-View, check drivers
   - ✅ Ja → Ga verder

3. **LED knippert bij button press?**
   - ❌ Nee → Check main.c button handling code
   - ✅ Ja → Ga verder

4. **USB data transfer OK?**
   - Test met Wireshark/USBPcap
   - Check endpoint configuration

---

## Performance Metrics

### Latency Test

**Setup**:
- Stopwatch of high-speed camera
- Meet tijd tussen button press en MIDI event

**Verwacht**:
- < 10ms latency (typisch 1-2ms)

### Throughput Test

**Test**: Stuur continu MIDI events
```c
while(1) {
    USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, 60, 127);
    HAL_Delay(10);
    USBD_MIDI_SendNoteOff(&hUsbDeviceFS, 0, 60, 64);
    HAL_Delay(10);
}
```

**Verwacht**:
- 50 Note ON/OFF pairs per seconde
- Geen USB errors
- Consistent packet delivery

---

## Troubleshooting Matrix

| Symptoom | Mogelijke Oorzaak | Oplossing |
|----------|-------------------|-----------|
| Device niet zichtbaar | JP1 nog geplaatst | Verwijder JP1 |
| "Unknown Device" | USB clock != 48MHz | Check clock config |
| Device reset loop | Firmware error | Check Error_Handler() |
| No MIDI messages | Endpoint niet open | Check USBD_MIDI_Init() |
| Wrong note values | Incorrect packet format | Verify packet structure |
| Intermittent connection | Bad USB cable | Replace cable |

---

## Deliverable Template

```markdown
# STM32H533RE USB MIDI Device - Test Results

## Hardware Setup
- Board: NUCLEO-H533RE
- Jumper JP1: REMOVED
- USB Connection: CN10 (User USB)
- Power: USB VBUS (5V)

## Device Recognition
[Screenshot 1: Device Manager with USB Audio Device visible]

Verified:
- VID: 0x0483
- PID: 0x5740
- Device Class: Audio

## MIDI Functionality
[Screenshot 2: MIDI-View device selection]

Device "STM32 MIDI Device" detected and enabled.

[Screenshot 3: MIDI-View with Note ON/OFF messages]

Test results:
- Note ON messages: ✅ Received
- Note OFF messages: ✅ Received
- Channel: 1 (correct)
- Note: 60 (Middle C, correct)
- Velocity: ON=127, OFF=64 (correct)

## Source Code
Full source code with comments attached:
- main.c
- usbd_midi.c
- usbd_midi.h
- usbd_desc.c

## Conclusion
✅ STM32H533RE successfully configured as USB MIDI Class device
✅ Note messages correctly transmitted
✅ Device recognized by MIDI software
```

---

## Next Steps (Optional Enhancements)

1. **Multiple Notes**: Different notes per button
2. **Velocity Sensitivity**: ADC input for velocity
3. **MIDI IN**: Receive and process MIDI from host
4. **SysEx**: Custom System Exclusive messages
5. **Multiple Cables**: 16 virtual MIDI ports
6. **LED Matrix**: Visual feedback for MIDI activity
