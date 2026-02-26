# Troubleshooting Guide - STM32 USB MIDI

## Index

1. [Device Recognition Problems](#device-recognition-problems)
2. [USB Communication Issues](#usb-communication-issues)
3. [MIDI Message Problems](#midi-message-problems)
4. [Hardware Issues](#hardware-issues)
5. [Software/Build Issues](#softwarebuild-issues)
6. [Advanced Debugging](#advanced-debugging)

---

## Device Recognition Problems

### ❌ "Unknown USB Device" in Device Manager

**Symptomen**:
- Device verschijnt met geel waarschuwingsicoon
- "Unknown USB Device (Device Descriptor Request Failed)"

**Mogelijke oorzaken & oplossingen**:

#### 1. USB Clock niet correct (48 MHz)

**Check**:
```c
// In SystemClock_Config()
RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};
PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;  // MOET 48 MHz zijn!
```

**Oplossing**:
- Open STM32CubeMX
- Clock Configuration tab
- Verifieer dat USB Clock = 48.000 MHz
- Use HSI48 of PLL configuratie voor exactly 48 MHz

#### 2. USB Pins niet correct geconfigureerd

**Check in main.c**:
```c
// USB pins moeten NIET manueel als GPIO geconfigureerd worden!
// STM32 HAL doet dit automatisch
```

**Oplossing**:
- Verwijder manuele GPIO config voor PA11/PA12
- Laat USB HAL de pins configureren

#### 3. Descriptor errors

**Verify**:
- `USBD_MIDI_CfgDesc` in usbd_midi.c
- wTotalLength moet kloppen (101 bytes)
- Alle descriptor lengths correct

**Debug methode**:
```c
// Add debug print in USBD_MIDI_GetCfgDesc()
static uint8_t *USBD_MIDI_GetCfgDesc(uint16_t *length)
{
  *length = (uint16_t)sizeof(USBD_MIDI_CfgDesc);
  // ADD: printf("Config desc size: %d\n", *length);
  return USBD_MIDI_CfgDesc;
}
```

---

### ❌ Device niet zichtbaar in Device Manager

**Symptomen**:
- Helemaal geen device in Device Manager
- Geen enumerate sound

**Checklist**:

1. **Hardware connections**
   ```
   ☐ USB kabel aangesloten op CN10 (niet CN1!)
   ☐ JP1 jumper VERWIJDERD
   ☐ Groene power LED brandt
   ```

2. **USB kabel test**
   - Probeer andere USB kabel (sommige kabels hebben geen data lijnen!)
   - Test kabel met ander USB device

3. **USB poort test**
   - Probeer andere USB poort op computer
   - Voorkeursvoorkeur: direct poort (niet via hub)

4. **VBUS check**
   - Meet met multimeter: Pin 1 van CN10 = 5V
   - Check schematics voor VBUS routing

---

### ❌ "USB Device Not Recognized" error

**Windows error message**:
> "USB device not recognized. The last USB device you connected to this computer malfunctioned..."

**Mogelijke oorzaken**:

#### 1. USB Enumeration mislukt

**Debug**:
- Check of `USBD_Start()` succesvol returnt
- Voeg LED toggle toe bij USB events

```c
// In usb_device.c
void MX_USB_DEVICE_Init(void)
{
  if (USBD_Init(&hUsbDeviceFS, &FS_Desc, DEVICE_FS) != USBD_OK)
  {
    // ADD: LED blink to indicate error
    while(1) { HAL_GPIO_TogglePin(LED_PORT, LED_PIN); HAL_Delay(100); }
  }
  
  if (USBD_RegisterClass(&hUsbDeviceFS, &USBD_MIDI) != USBD_OK)
  {
    while(1) { HAL_GPIO_TogglePin(LED_PORT, LED_PIN); HAL_Delay(200); }
  }
  
  if (USBD_Start(&hUsbDeviceFS) != USBD_OK)
  {
    while(1) { HAL_GPIO_TogglePin(LED_PORT, LED_PIN); HAL_Delay(300); }
  }
}
```

#### 2. Firmware crashed tijdens boot

**Check**:
- Does LED blink pattern work?
- Try flashing minimal code (just LED blink)
- Check for HardFault_Handler() calls

**Solution**:
```c
// Add in main()
int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  
  // LED test: Flash 3 times to indicate firmware running
  for(int i = 0; i < 3; i++) {
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
    HAL_Delay(200);
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
    HAL_Delay(200);
  }
  
  MX_USB_DEVICE_Init();  // Now init USB
  
  while (1) { ... }
}
```

---

## USB Communication Issues

### ❌ Device enumereert, maar geen MIDI messages ontvangen

**Symptomen**:
- Device zichtbaar in Device Manager als "USB Audio Device"
- MIDI-View ziet device
- Geen MIDI messages bij button press

**Debug stappen**:

#### 1. Check USB endpoints geopend

**Verify in USBD_MIDI_Init()**:
```c
static uint8_t USBD_MIDI_Init(USBD_HandleTypeDef *pdev, uint8_t cfgidx)
{
  // ... allocate memory ...
  
  /* Open Bulk IN endpoint */
  USBD_LL_OpenEP(pdev, MIDI_IN_EP, USBD_EP_TYPE_BULK, MIDI_DATA_IN_PACKET_SIZE);
  pdev->ep_in[MIDI_IN_EP & 0xFU].is_used = 1U;
  
  // ADD DEBUG:
  if (pdev->ep_in[MIDI_IN_EP & 0xFU].is_used == 0) {
    // ERROR: Endpoint not opened!
  }
  
  return USBD_OK;
}
```

#### 2. Check button reading

**Test button directly**:
```c
// In main loop
while (1)
{
  uint8_t button = HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN);
  
  // ADD: Toggle LED to show button state
  if (button == 0) {
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
  } else {
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
  }
  
  HAL_Delay(10);
}
```

#### 3. Check MIDI send function returns OK

```c
if (button_state == 0)
{
  uint8_t result = USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MAX);
  
  // ADD: Check result
  if (result == USBD_OK) {
    // Blink LED: Success
    HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
  } else if (result == USBD_BUSY) {
    // Previous transmission still in progress
  } else {
    // USBD_FAIL: Error occurred
  }
}
```

#### 4. Verify USB transmission state

```c
uint8_t USBD_MIDI_SendData(USBD_HandleTypeDef *pdev, uint8_t *data, uint16_t length)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDef *)pdev->pClassData;

  if (hmidi == NULL)
  {
    // ADD: Error indication
    return (uint8_t)USBD_FAIL;
  }

  if (hmidi->tx_state == 0U)
  {
    hmidi->tx_length = length;
    hmidi->tx_state = 1U;

    // ADD: Debug point
    USBD_LL_Transmit(pdev, MIDI_IN_EP, data, length);

    return (uint8_t)USBD_OK;
  }
  else
  {
    // ADD: Track how often this happens
    return (uint8_t)USBD_BUSY;
  }
}
```

---

### ❌ USB disconnects/reconnects randomly

**Symptomen**:
- Device disconnect sound
- Device Manager shows device disappearing/reappearing

**Mogelijke oorzaken**:

#### 1. Power issues

**Check**:
```
☐ USB port provides enough current (min 100mA)
☐ No other high-power devices on same USB hub
☐ Ferrite bead on USB cable (reduces noise)
```

**Solution**: Use powered USB hub or different PC USB port

#### 2. Watchdog reset

**Check**:
```c
// In main(), disable watchdog if enabled
// Comment out IWDG initialization
```

#### 3. Clock instability

**Solution**:
- Use HSI48 instead of PLL for USB clock (more stable)
- Check HSE crystal is oscillating (if used)

---

## MIDI Message Problems

### ❌ Note ON ontvangen, geen Note OFF

**Debug**:
```c
// Add explicit tracking
uint8_t note_playing = 0;

if (button_state == 0) {  // Pressed
  if (!note_playing) {
    USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MAX);
    note_playing = 1;
  }
} else {  // Released
  if (note_playing) {
    USBD_MIDI_SendNoteOff(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MED);
    note_playing = 0;
  }
}
```

### ❌ Wrong note number ontvangen

**Check packet construction**:
```c
uint8_t USBD_MIDI_SendNoteOn(USBD_HandleTypeDef *pdev, uint8_t channel, 
                              uint8_t note, uint8_t velocity)
{
  uint8_t midi_packet[4];

  // ADD: Validate inputs
  if (note > 127) return USBD_FAIL;
  if (velocity > 127) return USBD_FAIL;
  if (channel > 15) return USBD_FAIL;

  midi_packet[0] = (MIDI_CIN_NOTE_ON << 4) | (channel & 0x0F);
  midi_packet[1] = MIDI_STATUS_NOTE_ON | (channel & 0x0F);
  midi_packet[2] = note & 0x7F;
  midi_packet[3] = velocity & 0x7F;

  // ADD: Debug print
  // printf("Sending: %02X %02X %02X %02X\n", 
  //        midi_packet[0], midi_packet[1], midi_packet[2], midi_packet[3]);

  return USBD_MIDI_SendData(pdev, midi_packet, 4);
}
```

---

## Hardware Issues

### ❌ LED niet reageert

**Check**:
1. LED pin correct: PA5
2. LED polarity: Green LED is active HIGH
3. GPIO init called before LED write

**Test**:
```c
// Standalone LED test (in main, before while loop)
for (int i = 0; i < 5; i++) {
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
  HAL_Delay(500);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
  HAL_Delay(500);
}
```

### ❌ Button niet reageert

**Check**:
1. Button pin: PC13 (correct?)
2. Pull-up enabled
3. Button is active LOW

**Test**:
```c
// Read raw button state
while (1) {
  uint8_t state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13);
  // state == 0 when pressed, state == 1 when released
  
  // Toggle LED based on button
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, !state);  // Invert: LED on when pressed
  
  HAL_Delay(10);
}
```

---

## Software/Build Issues

### ❌ Compiler errors: "undefined reference to..."

**Common errors**:

#### Error: `undefined reference to 'USBD_MIDI'`

**Cause**: usbd_midi.c not compiled or linked

**Solution**:
1. Check that `usbd_midi.c` is in project
2. Refresh project (F5 STM32CubeIDE)
3. Clean build (Project → Clean)
4. Rebuild (Ctrl+B)

#### Error: `undefined reference to 'FS_Desc'`

**Cause**: usbd_desc.c missing or not compiled

**Solution**:
- Add `USB_DEVICE/App/usbd_desc.c` to project
- Check includes in main.c: `#include "usbd_desc.h"`

### ❌ HAL library errors

**Common**:
```
error: 'USBD_HandleTypeDef' has no member named 'pClassData'
```

**Cause**: Wrong HAL version or missing includes

**Solution**:
1. Update STM32CubeH5 package (Help → Manage Embedded Software Packages)
2. Check includes in usbd_midi.c:
   ```c
   #include "usbd_midi.h"
   #include "usbd_ctlreq.h"
   #include "usbd_ioreq.h"
   ```

---

## Advanced Debugging

### Use SWO (Serial Wire Output)

**Setup**:
1. Enable SWO in Debug Configuration
2. Add printf redirect:

```c
// In main.c
#include <stdio.h>

int _write(int file, char *ptr, int len)
{
  for(int i = 0; i < len; i++)
    ITM_SendChar((*ptr++));
  return len;
}

// Then use:
printf("USB Init: %d\n", result);
```

### Use Debug Breakpoints

**Key locations**:
1. `USBD_MIDI_Init()` - Check if called
2. `USBD_MIDI_SendData()` - Check if reached
3. `USBD_MIDI_DataIn()` - Check TX complete callback
4. `USBD_LL_Transmit()` - Check low-level USB transmit

### Analyze with Logic Analyzer

**For USB D+/D- signals**:
- Expensive but definitive
- Shows exact USB traffic
- Can decode USB packets

**Alternative**: Use USBPcap + Wireshark (software solution)

---

## Quick Reference: Error Check Flow

```
┌─────────────────────────────────────┐
│ Device not recognized?              │
└──────────┬──────────────────────────┘
           │
           ├─ Check hardware (JP1, CN10, cable)
           ├─ Check USB clock (48 MHz)
           └─ Check descriptors (wTotalLength)
           
┌─────────────────────────────────────┐
│ Device recognized, no MIDI?         │
└──────────┬──────────────────────────┘
           │
           ├─ Check button reading (LED test)
           ├─ Check MIDI packet format
           ├─ Check endpoint opened
           └─ Check TX state machine
           
┌─────────────────────────────────────┐
│ Wrong MIDI data?                    │
└──────────┬──────────────────────────┘
           │
           ├─ Validate packet bytes
           ├─ Check CIN value
           └─ Check status byte

┌─────────────────────────────────────┐
│ Random disconnects?                 │
└──────────┬──────────────────────────┘
           │
           ├─ Check power supply
           ├─ Check for HardFault
           └─ Check clock stability
```

---

## Getting Help

### Information to provide:

1. **Hardware**:
   - Board revision
   - Jumper settings
   - USB port used

2. **Software**:
   - STM32CubeIDE version
   - STM32CubeH5 package version
   - Clock configuration (screenshot from CubeMX)

3. **Symptoms**:
   - Device Manager screenshot
   - MIDI-View screenshot (if applicable)
   - Error messages

4. **What you tried**:
   - Steps already attempted
   - Results of tests

### Resources:

- **ST Community Forums**: https://community.st.com/
- **USB.org MIDI Spec**: https://www.usb.org/document-library/usb-midi-devices-10
- **STM32 USB Training**: ST website training materials
- **GitHub Issues**: (If this were a published library)

---

## Success Indicators

✅ **Everything works when**:
- Device shows as "USB Audio Device" in Device Manager
- VID/PID = 0x0483/0x5740
- MIDI-View lists "STM32 MIDI Device"
- Button press → LED on → Note ON in MIDI-View
- Button release → LED off → Note OFF in MIDI-View
- Consistent timing and no errors

🎉 **Congratulations! Your STM32 is now a MIDI controller!**
