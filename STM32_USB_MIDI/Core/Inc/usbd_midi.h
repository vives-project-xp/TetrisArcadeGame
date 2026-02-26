/**
  ******************************************************************************
  * @file    usbd_midi.h
  * @brief   Header file for USB MIDI Class implementation
  * @author  Project Experience 2.2
  * @date    2026
  ******************************************************************************
  * @attention
  *
  * USB MIDI Class implementation voor STM32H533RE
  * Gebaseerd op USB Device Middleware en USB Audio MIDI Class specification
  *
  ******************************************************************************
  */

#ifndef __USBD_MIDI_H
#define __USBD_MIDI_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "usbd_ioreq.h"

/* USB MIDI Class Codes */
#define USB_DEVICE_CLASS_AUDIO                  0x01
#define AUDIO_SUBCLASS_AUDIOCONTROL             0x01
#define AUDIO_SUBCLASS_MIDISTREAMING            0x03

/* USB MIDI Descriptor Types */
#define AUDIO_DESCRIPTOR_TYPE_INTERFACE         0x24
#define AUDIO_DESCRIPTOR_TYPE_ENDPOINT          0x25

/* USB MIDI Descriptor Subtypes */
#define AUDIO_CONTROL_HEADER                    0x01
#define MIDI_IN_JACK                            0x02
#define MIDI_OUT_JACK                           0x03

/* MIDI Jack Types */
#define MIDI_JACK_TYPE_EMBEDDED                 0x01
#define MIDI_JACK_TYPE_EXTERNAL                 0x02

/* USB MIDI Configuration */
#define MIDI_IN_EP                              0x81  /* Endpoint 1 IN */
#define MIDI_OUT_EP                             0x01  /* Endpoint 1 OUT */
#define MIDI_DATA_IN_PACKET_SIZE                64
#define MIDI_DATA_OUT_PACKET_SIZE               64

/* MIDI Device Parameters */
#define MIDI_BCD_NUM                            0x0100  /* MIDI v1.0 */
#define USBD_MIDI_CONFIG_DESC_SIZE              101     /* Total descriptor size */

/* USB MIDI Cable Number and Code Index Numbers (CIN) */
#define MIDI_CIN_MISC                           0x00
#define MIDI_CIN_CABLE_EVENT                    0x01
#define MIDI_CIN_SYSTEM_2BYTE                   0x02
#define MIDI_CIN_SYSTEM_3BYTE                   0x03
#define MIDI_CIN_SYSEX_START                    0x04
#define MIDI_CIN_SYSEX_END_1BYTE                0x05
#define MIDI_CIN_SYSEX_END_2BYTE                0x06
#define MIDI_CIN_SYSEX_END_3BYTE                0x07
#define MIDI_CIN_NOTE_OFF                       0x08
#define MIDI_CIN_NOTE_ON                        0x09
#define MIDI_CIN_POLY_KEYPRESS                  0x0A
#define MIDI_CIN_CONTROL_CHANGE                 0x0B
#define MIDI_CIN_PROGRAM_CHANGE                 0x0C
#define MIDI_CIN_CHANNEL_PRESSURE               0x0D
#define MIDI_CIN_PITCH_BEND                     0x0E
#define MIDI_CIN_SINGLE_BYTE                    0x0F

/* MIDI Message Status Bytes */
#define MIDI_STATUS_NOTE_OFF                    0x80
#define MIDI_STATUS_NOTE_ON                     0x90
#define MIDI_STATUS_POLY_PRESSURE               0xA0
#define MIDI_STATUS_CONTROL_CHANGE              0xB0
#define MIDI_STATUS_PROGRAM_CHANGE              0xC0
#define MIDI_STATUS_CHANNEL_PRESSURE            0xD0
#define MIDI_STATUS_PITCH_BEND                  0xE0

/* MIDI Notes */
#define MIDI_NOTE_C4                            60  /* Middle C */
#define MIDI_NOTE_C_SHARP_4                     61
#define MIDI_NOTE_D4                            62
#define MIDI_NOTE_D_SHARP_4                     63
#define MIDI_NOTE_E4                            64
#define MIDI_NOTE_F4                            65
#define MIDI_NOTE_F_SHARP_4                     66
#define MIDI_NOTE_G4                            67
#define MIDI_NOTE_G_SHARP_4                     68
#define MIDI_NOTE_A4                            69
#define MIDI_NOTE_A_SHARP_4                     70
#define MIDI_NOTE_B4                            71
#define MIDI_NOTE_C5                            72

/* MIDI Velocity */
#define MIDI_VELOCITY_MAX                       127
#define MIDI_VELOCITY_MED                       64
#define MIDI_VELOCITY_OFF                       0

/* USB MIDI Packet structure (4 bytes) */
typedef struct
{
  uint8_t cable_number : 4;  /* Cable number (0-15) */
  uint8_t code_index : 4;    /* Code Index Number (CIN) */
  uint8_t midi_0;            /* MIDI status byte */
  uint8_t midi_1;            /* MIDI data byte 1 */
  uint8_t midi_2;            /* MIDI data byte 2 */
} __attribute__((packed)) USB_MIDI_Packet_t;

/* MIDI Class Handle structure */
typedef struct
{
  uint32_t alt_setting;
  uint8_t  tx_buffer[MIDI_DATA_IN_PACKET_SIZE];
  uint8_t  rx_buffer[MIDI_DATA_OUT_PACKET_SIZE];
  uint32_t tx_length;
  uint32_t rx_length;
  uint8_t  tx_state;
  uint8_t  rx_state;
} USBD_MIDI_HandleTypeDef;

/* External declarations */
extern USBD_ClassTypeDef USBD_MIDI;

/* Function prototypes */
uint8_t USBD_MIDI_SendData(USBD_HandleTypeDef *pdev, uint8_t *data, uint16_t length);
uint8_t USBD_MIDI_SendNoteOn(USBD_HandleTypeDef *pdev, uint8_t channel, uint8_t note, uint8_t velocity);
uint8_t USBD_MIDI_SendNoteOff(USBD_HandleTypeDef *pdev, uint8_t channel, uint8_t note, uint8_t velocity);
uint8_t USBD_MIDI_SendControlChange(USBD_HandleTypeDef *pdev, uint8_t channel, uint8_t control, uint8_t value);

#ifdef __cplusplus
}
#endif

#endif /* __USBD_MIDI_H */
