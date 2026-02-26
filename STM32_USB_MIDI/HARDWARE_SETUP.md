# Hardware Setup Guide - Nucleo-H533RE USB MIDI

## Stap-voor-stap Hardware Configuratie

### Stap 1: Disconnect ST-Link Voeding

De Nucleo-H533RE heeft twee voedingsmogelijkheden:
1. Via ST-Link (CN1 USB connector)
2. Via User USB (CN10 USB connector)

Voor USB MIDI moeten we de User USB gebruiken.

#### Jumper JP1 (Power Selection)
```
ST-Link Voeding (standaard):  |===|     (jumper geplaatst)
USB User Voeding (nodig):     |   |     (jumper VERWIJDERD)

Locatie: Nabij de ST-Link connector aan de bovenkant van het bord
```

**Actie**: Verwijder de jumper van JP1 volledig voor USB voeding

### Stap 2: IDD Measurement Jumper

#### Jumper JP2
```
ON positie (normaal):    |===|
OFF positie:             |   |

Locatie: Bij de IDD measurement pads
```

**Actie**: Zorg dat JP2 in de ON positie staat (jumper geplaatst)

### Stap 3: USB Connector Identificatie

Het Nucleo-H533RE bord heeft twee USB connectors:

```
┌─────────────────────────────────┐
│  [ST-Link]          Nucleo-64   │
│    CN1 ◄─── Voor programmeren   │
│                                  │
│                                  │
│  [User USB]                      │
│    CN10 ◄─── Voor MIDI Device   │
│                                  │
│                          [H533RE]│
│                                  │
│  ○ PC13 (User Button)            │
│  ○ LED (PA5)                     │
└─────────────────────────────────┘
```

**Let op**: 
- **CN1** (bovenkant): ST-Link USB - voor programmeren
- **CN10** (onderkant): User USB - voor MIDI functionaliteit

### Stap 4: Programmeer Procedure

1. **Flash de firmware via ST-Link**:
   - Sluit CN1 aan op je computer
   - JP1 kan nog geplaatst zijn
   - Open STM32CubeIDE
   - Build en flash het project (Run → Debug)

2. **Switch naar User USB**:
   - Disconnect CN1 USB kabel
   - **Verwijder JP1 jumper**
   - Sluit CN10 aan op je computer
   - Reset het bord (zwarte RESET knop)

### Stap 5: Verificatie

#### Windows Device Manager Check
1. Open Device Manager (`devmgmt.msc`)
2. Kijk onder:
   - **Sound, video and game controllers**
     - Je zou "USB Audio Device" moeten zien
   - Of onder **Universal Serial Bus devices**

#### MIDI-View Verificatie
1. Open MIDI-View software
2. Ga naar Options → MIDI Devices
3. Je zou "STM32 MIDI Device" moeten zien in de Input lijst

### Stap 6: Test met User Button

- Druk op de **blauwe USER button** (PC13)
- In MIDI-View zou je moeten zien:
  ```
  Note ON: Channel 1, Note 60 (Middle C), Velocity 127
  Note OFF: Channel 1, Note 60, Velocity 64
  ```

## Pinout Overzicht

### USB Pins (automatisch geconfigureerd)
```
CN10 USB Connector:
  Pin 1: VBUS (5V)
  Pin 2: D- (PA11/USB_DM)
  Pin 3: D+ (PA12/USB_DP)
  Pin 4: GND
```

### User Input
```
PC13: User Button (blauw) - Pull-up, active LOW
```

### Status LED (optioneel)
```
PA5: Green LED (LD2) - STM32 Nucleo board LED
```

## Power Budget

USB Full-Speed voeding:
- **Maximum**: 500mA @ 5V (USB 2.0)
- **STM32H533RE verbruik**: ~50-100mA (afhankelijk van clock speed)
- **Beschikbaar**: Voldoende voor USB MIDI applicatie

## Troubleshooting Hardware

### Probleem: Device wordt niet herkend
**Checklist**:
- [ ] Is JP1 verwijderd?
- [ ] Is USB kabel aangesloten op CN10 (niet CN1)?
- [ ] Is de firmware correct geflasht?
- [ ] Is het bord gereset na het verwisselen van USB kabel?

### Probleem: Instabiele USB verbinding
**Mogelijke oorzaken**:
- Slechte USB kabel (gebruik kabel met data lijnen)
- Onvoldoende voeding (test andere USB poort)
- USB clock niet correct (controleer 48 MHz clock configuratie)

### Probleem: Bord reageert niet
**Oplossing**:
1. Druk op zwarte RESET knop
2. Als dat niet werkt: Plaats JP1 terug, sluit ST-Link aan, flash firmware opnieuw

## Schema Referentie

Voor gedetailleerde schema's, zie:
- [Nucleo-H533RE Schematic (MB1813)](https://www.st.com/resource/en/schematic_pack/mb1813-h533re-c01-schematic.pdf)

Relevante secties:
- Figure 4: Power supply
- Figure 6: USB connectors
- Table 5: Jumper configuration
