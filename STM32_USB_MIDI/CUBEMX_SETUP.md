# STM32CubeMX Configuration Guide

## Stap-voor-stap Setup voor USB MIDI Project

### Stap 1: Nieuw Project Aanmaken

1. Open **STM32CubeMX**
2. Klik op **File → New Project**
3. Selecteer:
   - Board Selector tab
   - Type: Nucleo-64
   - MCU/MPU Series: STM32H5
   - Board: **NUCLEO-H533RE**
4. Klik **Start Project**
5. Kies **Yes** om de standaard pinout te initialiseren

---

### Stap 2: System Core Configuratie

#### RCC (Reset and Clock Control)

1. Navigeer naar **System Core → RCC**
2. Configuratie:
   ```
   High Speed Clock (HSE): BYPASS Clock Source
   Low Speed Clock (LSE): Disabled
   Master Clock Output 1: Disabled
   ```
   
   **Uitleg**: BYPASS betekent dat we de 8 MHz clock van de ST-Link MCO gebruiken

---

### Stap 3: Clock Configuration

1. Klik op de **Clock Configuration** tab
2. Configureer als volgt:

#### Input Clock
- **HSE**: 8 MHz (automatisch ingesteld door Board config)
- **HSI48**: Enable (voor USB)

#### PLL Configuration (PLL1)
```
Input frequency: HSE (8 MHz)
/M: 2          → VCO input = 4 MHz
×N: 125        → VCO output = 500 MHz
/P: 2          → SYSCLK = 250 MHz
/Q: 2
/R: 2
```

#### USB Clock
```
USB Clock Mux: HSI48 (48 MHz)
✓ BELANGRIJK: USB MOET exact 48 MHz zijn!
```

#### Bus Clocks
```
HCLK (AHB):   250 MHz
APB1:         250 MHz
APB2:         250 MHz
APB3:         250 MHz
```

**Visuele verificatie**: Alle lijnen moeten groen zijn zonder waarschuwingen

---

### Stap 4: USB Configuration

#### USB Peripheral

1. Navigeer naar **Connectivity → USB**
2. Mode: **Device_Only**
3. Parameter Settings:
   ```
   Device Speed: Full Speed 12Mb/s
   phy: Embedded Phy Full Speed
   Link Power Management: Disabled
   Battery Charging: Disabled
   VBUS sensing: Disabled
   SOF output: Disabled
   ```

#### USB GPIO Pins (automatisch geconfigureerd)
```
PA11: USB_DM  (Data Minus)
PA12: USB_DP  (Data Plus)
```

**Let op**: VBUS sensing is disabled omdat we VBUS niet uitlezen

---

### Stap 5: Middleware → USB_DEVICE

1. Navigeer naar **Middleware → USB_DEVICE**
2. **Class For FS IP**: Selecteer **Audio** (wijst naar Audio class)
   
   **Belangrijk**: We gebruiken de Audio class omdat MIDI een subclass is van Audio.
   Later vervangen we dit met onze custom MIDI implementatie.

3. Parameter Settings:
   ```
   - Laat standaard settings staan
   - Opmerking: We overschrijven dit later met usbd_midi.c
   ```

**Alternatief**: Je kunt ook "Custom HID" kiezen; we vervangen het toch

---

### Stap 6: GPIO Configuration

#### User Button (PC13)

De User Button is al geconfigureerd door de board setup, maar controleer:

1. Navigeer naar **System Core → GPIO**
2. Zoek **PC13** in de pin lijst
3. Configuratie zou moeten zijn:
   ```
   GPIO mode: Input mode
   GPIO Pull-up/Pull-down: Pull-up
   User Label: B1 [Blue PushButton]
   ```

#### LED (PA5)

Ook automatisch geconfigureerd:

```
GPIO mode: Output Push Pull
GPIO Pull-up/Pull-down: No pull-up and no pull-down
Maximum output speed: Low
User Label: LD2 [Green Led]
```

---

### Stap 7: NVIC Settings

1. Navigeer naar **System Core → NVIC**
2. Controleer dat **USB DRD FS global interrupt** enabled is
3. Priority: Default (Priority 0, SubPriority 0) is OK

---

### Stap 8: Project Settings

1. Klik op **Project → Settings** (of het tandwiel icoon)
2. Configureer:

#### Project Tab
```
Project Name: STM32_USB_MIDI
Project Location: [Jouw workspace pad]
Toolchain / IDE: STM32CubeIDE
```

#### Code Generator Tab
```
STM32Cube Firmware Library Package: [Latest H5 package]

Generated files:
☑ Generate peripheral initialization as a pair of .c/.h files per peripheral
☑ Backup previously generated files when re-generating
☑ Keep User Code when re-generating
☐ Delete previously generated files when not re-generated

HAL Settings:
☑ Set all free pins as analog (for power consumption)
☐ Enable Full Assert
```

---

### Stap 9: Generate Code

1. Klik op **Project → Generate Code** (of Ctrl+Shift+G)
2. Wacht tot code generatie klaar is
3. Klik **Open Project** om het project in STM32CubeIDE te openen

---

### Stap 10: Custom MIDI Code Integreren

Na code generatie moet je de custom MIDI bestanden toevoegen:

#### Bestanden om toe te voegen:

1. **Core/Inc/usbd_midi.h**
2. **Core/Src/usbd_midi.c**
3. **Core/Src/main.c** (vervangen)

#### In STM32CubeIDE:

1. **Refresh** het project (F5)
2. Kopieer de bestanden naar de juiste mappen
3. **Vervang main.c** met de custom implementatie
4. **Vervang** in `USB_DEVICE/App/usb_device.c`:
   
   Zoek:
   ```c
   #include "usbd_audio.h"  // Of usbd_hid.h
   ```
   
   Vervang door:
   ```c
   #include "usbd_midi.h"
   ```
   
   Zoek:
   ```c
   USBD_RegisterClass(&hUsbDeviceFS, &USBD_AUDIO);
   ```
   
   Vervang door:
   ```c
   USBD_RegisterClass(&hUsbDeviceFS, &USBD_MIDI);
   ```

---

### Stap 11: Build en Test

1. **Build Project** (Ctrl+B of hammer icon)
2. Controleer dat er geen compiler errors zijn
3. **Flash** via ST-Link (Run → Debug of F11)
4. **Disconnect ST-Link**
5. **Verwijder JP1 jumper**
6. **Sluit USB User connector (CN10) aan**
7. Test met MIDI-View

---

## Troubleshooting STM32CubeMX

### USB Clock niet 48 MHz

**Probleem**: Rode waarschuwing bij USB clock
**Oplossing**: 
- Enable **HSI48** in RCC configuratie
- Selecteer HSI48 als USB clock source

### Build Errors na code generatie

**Probleem**: Missing includes of undefined references
**Mogelijke oorzaken**:
1. USBD middleware niet correct geconfigureerd
2. HAL drivers niet gegenereerd
3. Old STM32Cube firmware package

**Oplossing**:
- Check **Help → Manage Embedded Software Packages**
- Update STM32CubeH5 firmware package naar latest versie
- Re-generate code

### USB Device niet herkend

**Check**:
1. ☑ USB Clock is 48 MHz
2. ☑ PA11/PA12 geconfigureerd voor USB
3. ☑ USB_DEVICE middleware enabled
4. ☑ Jumper settings correct (JP1 verwijderd)

---

## Handige Tips

### Pinout View

- Gebruik **Pinout view** om te zien welke pins in gebruik zijn
- Groen = geconfigureerd
- Geel = power pin
- Grijs = beschikbaar

### Conflict Resolution

- Als pins in conflict zijn, krijg je een waarschuwing
- CubeMX geeft suggesties voor alternatieve pins
- Voor USB zijn PA11/PA12 verplicht (geen alternatieven)

### Code Regeneration

- **Gebruik altijd USER CODE sections** in gegenereerde bestanden:
  ```c
  /* USER CODE BEGIN xxx */
  // Jouw eigen code hier
  /* USER CODE END xxx */
  ```
- Code binnen deze sections blijft behouden bij regeneratie

---

## Visuele Checklist

Voordat je code genereert, controleer:

- ✅ HSE: 8 MHz BYPASS
- ✅ HSI48: Enabled
- ✅ SYSCLK: 250 MHz
- ✅ USB Clock: 48 MHz (HSI48)
- ✅ USB Device_Only: Enabled
- ✅ PA11/PA12: USB functie
- ✅ PC13: Input met pull-up
- ✅ PA5: Output Push-Pull
- ✅ Project name en locatie ingesteld

Als alles groen is ✅, je bent klaar voor code generatie!
