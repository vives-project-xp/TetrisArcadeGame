/**
  ******************************************************************************
  * @file    usbd_midi.c
  * @brief   USB MIDI Class implementation for STM32H533RE
  * @author  Project Experience 2.2
  * @date    2026
  ******************************************************************************
  * @attention
  *
  * Deze file implementeert de USB MIDI Class volgens de USB Audio Device 
  * Class Specification for MIDI Devices, Release 1.0.
  *
  * De implementatie bevat:
  * - USB MIDI Descriptors (Device, Configuration, Interface, Endpoint)
  * - MIDI Class callbacks (Init, DeInit, Setup, DataIn, DataOut)
  * - Helper functies voor het versturen van MIDI berichten
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "usbd_midi.h"
#include "usbd_ctlreq.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/

/* Private function prototypes -----------------------------------------------*/
static uint8_t USBD_MIDI_Init(USBD_HandleTypeDef *pdev, uint8_t cfgidx);
static uint8_t USBD_MIDI_DeInit(USBD_HandleTypeDef *pdev, uint8_t cfgidx);
static uint8_t USBD_MIDI_Setup(USBD_HandleTypeDef *pdev, USBD_SetupReqTypeDefSTM32 *req);
static uint8_t USBD_MIDI_DataIn(USBD_HandleTypeDef *pdev, uint8_t epnum);
static uint8_t USBD_MIDI_DataOut(USBD_HandleTypeDef *pdev, uint8_t epnum);
static uint8_t USBD_MIDI_EP0_RxReady(USBD_HandleTypeDef *pdev);
static uint8_t *USBD_MIDI_GetCfgDesc(uint16_t *length);
static uint8_t *USBD_MIDI_GetDeviceQualifierDesc(uint16_t *length);

/**
  * @brief  USB MIDI Class Callbacks structure
  */
USBD_ClassTypeDef USBD_MIDI =
{
  USBD_MIDI_Init,
  USBD_MIDI_DeInit,
  USBD_MIDI_Setup,
  NULL,                     /* EP0_TxSent */
  USBD_MIDI_EP0_RxReady,
  USBD_MIDI_DataIn,
  USBD_MIDI_DataOut,
  NULL,                     /* SOF */
  NULL,                     /* IsoINIncomplete */
  NULL,                     /* IsoOUTIncomplete */
  USBD_MIDI_GetCfgDesc,
  USBD_MIDI_GetCfgDesc,
  USBD_MIDI_GetCfgDesc,
  USBD_MIDI_GetDeviceQualifierDesc,
};

/**
  * @brief  USB MIDI Configuration Descriptor
  * 
  * Deze descriptor definieert de volledige USB MIDI interface structuur:
  * 1. Configuration Descriptor
  * 2. Audio Control Interface (vereist voor MIDI)
  * 3. MIDI Streaming Interface met embedded MIDI jacks
  * 4. Bulk endpoints voor MIDI data
  */
__ALIGN_BEGIN static uint8_t USBD_MIDI_CfgDesc[USBD_MIDI_CONFIG_DESC_SIZE] __ALIGN_END =
{
  /* Configuration Descriptor */
  0x09,                                 /* bLength */
  USB_DESC_TYPE_CONFIGURATION,          /* bDescriptorType: Configuration */
  LOBYTE(USBD_MIDI_CONFIG_DESC_SIZE),   /* wTotalLength */
  HIBYTE(USBD_MIDI_CONFIG_DESC_SIZE),
  0x02,                                 /* bNumInterfaces: 2 (Audio Control + MIDI Streaming) */
  0x01,                                 /* bConfigurationValue */
  0x00,                                 /* iConfiguration */
  0xC0,                                 /* bmAttributes: Self powered */
  0x32,                                 /* MaxPower: 100 mA */

  /***** Audio Control Interface *****/
  /* Standard AC Interface Descriptor */
  0x09,                                 /* bLength */
  USB_DESC_TYPE_INTERFACE,              /* bDescriptorType: Interface */
  0x00,                                 /* bInterfaceNumber: 0 */
  0x00,                                 /* bAlternateSetting */
  0x00,                                 /* bNumEndpoints: 0 (no endpoints) */
  USB_DEVICE_CLASS_AUDIO,               /* bInterfaceClass: Audio */
  AUDIO_SUBCLASS_AUDIOCONTROL,          /* bInterfaceSubClass: Audio Control */
  0x00,                                 /* bInterfaceProtocol */
  0x00,                                 /* iInterface */

  /* Class-Specific AC Interface Header Descriptor */
  0x09,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE (0x24) */
  AUDIO_CONTROL_HEADER,                 /* bDescriptorSubtype: HEADER */
  0x00, 0x01,                           /* bcdADC: Audio Device Class v1.0 */
  0x09, 0x00,                           /* wTotalLength: 9 bytes */
  0x01,                                 /* bInCollection: 1 streaming interface */
  0x01,                                 /* baInterfaceNr: Interface 1 (MIDI Streaming) */

  /***** MIDI Streaming Interface *****/
  /* Standard MS Interface Descriptor */
  0x09,                                 /* bLength */
  USB_DESC_TYPE_INTERFACE,              /* bDescriptorType: Interface */
  0x01,                                 /* bInterfaceNumber: 1 */
  0x00,                                 /* bAlternateSetting */
  0x02,                                 /* bNumEndpoints: 2 (Bulk IN + Bulk OUT) */
  USB_DEVICE_CLASS_AUDIO,               /* bInterfaceClass: Audio */
  AUDIO_SUBCLASS_MIDISTREAMING,         /* bInterfaceSubClass: MIDI Streaming (0x03) */
  0x00,                                 /* bInterfaceProtocol */
  0x00,                                 /* iInterface */

  /* Class-Specific MS Interface Header Descriptor */
  0x07,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE */
  AUDIO_CONTROL_HEADER,                 /* bDescriptorSubtype: MS_HEADER */
  0x00, 0x01,                           /* bcdMSC: MIDI Streaming Class v1.0 */
  0x41, 0x00,                           /* wTotalLength: 65 bytes */

  /* MIDI IN Jack Descriptor (Embedded) */
  0x06,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE */
  MIDI_IN_JACK,                         /* bDescriptorSubtype: MIDI_IN_JACK */
  MIDI_JACK_TYPE_EMBEDDED,              /* bJackType: Embedded */
  0x01,                                 /* bJackID: 1 */
  0x00,                                 /* iJack */

  /* MIDI IN Jack Descriptor (External) */
  0x06,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE */
  MIDI_IN_JACK,                         /* bDescriptorSubtype: MIDI_IN_JACK */
  MIDI_JACK_TYPE_EXTERNAL,              /* bJackType: External */
  0x02,                                 /* bJackID: 2 */
  0x00,                                 /* iJack */

  /* MIDI OUT Jack Descriptor (Embedded) */
  0x09,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE */
  MIDI_OUT_JACK,                        /* bDescriptorSubtype: MIDI_OUT_JACK */
  MIDI_JACK_TYPE_EMBEDDED,              /* bJackType: Embedded */
  0x03,                                 /* bJackID: 3 */
  0x01,                                 /* bNrInputPins: 1 */
  0x02,                                 /* baSourceID(1): External Jack 2 */
  0x01,                                 /* baSourcePin(1): Pin 1 */
  0x00,                                 /* iJack */

  /* MIDI OUT Jack Descriptor (External) */
  0x09,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_INTERFACE,      /* bDescriptorType: CS_INTERFACE */
  MIDI_OUT_JACK,                        /* bDescriptorSubtype: MIDI_OUT_JACK */
  MIDI_JACK_TYPE_EXTERNAL,              /* bJackType: External */
  0x04,                                 /* bJackID: 4 */
  0x01,                                 /* bNrInputPins: 1 */
  0x01,                                 /* baSourceID(1): Embedded Jack 1 */
  0x01,                                 /* baSourcePin(1): Pin 1 */
  0x00,                                 /* iJack */

  /***** Bulk OUT Endpoint (Host to Device) *****/
  /* Standard Bulk OUT Endpoint Descriptor */
  0x09,                                 /* bLength */
  USB_DESC_TYPE_ENDPOINT,               /* bDescriptorType: Endpoint */
  MIDI_OUT_EP,                          /* bEndpointAddress: OUT Endpoint 1 */
  0x02,                                 /* bmAttributes: Bulk */
  LOBYTE(MIDI_DATA_OUT_PACKET_SIZE),    /* wMaxPacketSize */
  HIBYTE(MIDI_DATA_OUT_PACKET_SIZE),
  0x00,                                 /* bInterval: ignored for Bulk */
  0x00,                                 /* bRefresh */
  0x00,                                 /* bSynchAddress */

  /* Class-Specific MS Bulk OUT Endpoint Descriptor */
  0x05,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_ENDPOINT,       /* bDescriptorType: CS_ENDPOINT */
  0x01,                                 /* bDescriptorSubtype: MS_GENERAL */
  0x01,                                 /* bNumEmbMIDIJack: 1 */
  0x01,                                 /* baAssocJackID(1): Embedded Jack 1 */

  /***** Bulk IN Endpoint (Device to Host) *****/
  /* Standard Bulk IN Endpoint Descriptor */
  0x09,                                 /* bLength */
  USB_DESC_TYPE_ENDPOINT,               /* bDescriptorType: Endpoint */
  MIDI_IN_EP,                           /* bEndpointAddress: IN Endpoint 1 */
  0x02,                                 /* bmAttributes: Bulk */
  LOBYTE(MIDI_DATA_IN_PACKET_SIZE),     /* wMaxPacketSize */
  HIBYTE(MIDI_DATA_IN_PACKET_SIZE),
  0x00,                                 /* bInterval: ignored for Bulk */
  0x00,                                 /* bRefresh */
  0x00,                                 /* bSynchAddress */

  /* Class-Specific MS Bulk IN Endpoint Descriptor */
  0x05,                                 /* bLength */
  AUDIO_DESCRIPTOR_TYPE_ENDPOINT,       /* bDescriptorType: CS_ENDPOINT */
  0x01,                                 /* bDescriptorSubtype: MS_GENERAL */
  0x01,                                 /* bNumEmbMIDIJack: 1 */
  0x03,                                 /* baAssocJackID(1): Embedded Jack 3 */
};

/**
  * @brief  Device Qualifier Descriptor
  */
__ALIGN_BEGIN static uint8_t USBD_MIDI_DeviceQualifierDesc[USB_LEN_DEV_QUALIFIER_DESC] __ALIGN_END =
{
  USB_LEN_DEV_QUALIFIER_DESC,
  USB_DESC_TYPE_DEVICE_QUALIFIER,
  0x00, 0x02,
  0x00,
  0x00,
  0x00,
  0x40,
  0x01,
  0x00,
};

/* Private functions ---------------------------------------------------------*/

/**
  * @brief  USBD_MIDI_Init
  *         Initialize the MIDI interface
  * @param  pdev: Device handle
  * @param  cfgidx: Configuration index
  * @retval Status
  */
static uint8_t USBD_MIDI_Init(USBD_HandleTypeDef *pdev, uint8_t cfgidx)
{
  UNUSED(cfgidx);
  USBD_MIDI_HandleTypeDef *hmidi;

  /* Allocate MIDI structure */
  hmidi = (USBD_MIDI_HandleTypeDef *)USBD_malloc(sizeof(USBD_MIDI_HandleTypeDef));

  if (hmidi == NULL)
  {
    return (uint8_t)USBD_EMEM;
  }

  pdev->pClassData = (void *)hmidi;

  /* Initialize MIDI handle structure */
  hmidi->alt_setting = 0;
  hmidi->tx_state = 0;
  hmidi->rx_state = 0;
  hmidi->tx_length = 0;
  hmidi->rx_length = 0;

  /* Open Bulk IN endpoint */
  (void)USBD_LL_OpenEP(pdev, MIDI_IN_EP, USBD_EP_TYPE_BULK, MIDI_DATA_IN_PACKET_SIZE);
  pdev->ep_in[MIDI_IN_EP & 0xFU].is_used = 1U;

  /* Open Bulk OUT endpoint */
  (void)USBD_LL_OpenEP(pdev, MIDI_OUT_EP, USBD_EP_TYPE_BULK, MIDI_DATA_OUT_PACKET_SIZE);
  pdev->ep_out[MIDI_OUT_EP & 0xFU].is_used = 1U;

  /* Prepare endpoint to receive data */
  (void)USBD_LL_PrepareReceive(pdev, MIDI_OUT_EP, hmidi->rx_buffer, 
                                MIDI_DATA_OUT_PACKET_SIZE);

  return (uint8_t)USBD_OK;
}

/**
  * @brief  USBD_MIDI_DeInit
  *         DeInitialize the MIDI layer
  * @param  pdev: Device handle
  * @param  cfgidx: Configuration index
  * @retval Status
  */
static uint8_t USBD_MIDI_DeInit(USBD_HandleTypeDef *pdev, uint8_t cfgidx)
{
  UNUSED(cfgidx);

  /* Close Bulk endpoints */
  (void)USBD_LL_CloseEP(pdev, MIDI_IN_EP);
  pdev->ep_in[MIDI_IN_EP & 0xFU].is_used = 0U;

  (void)USBD_LL_CloseEP(pdev, MIDI_OUT_EP);
  pdev->ep_out[MIDI_OUT_EP & 0xFU].is_used = 0U;

  /* Free allocated memory */
  if (pdev->pClassData != NULL)
  {
    USBD_free(pdev->pClassData);
    pdev->pClassData = NULL;
  }

  return (uint8_t)USBD_OK;
}

/**
  * @brief  USBD_MIDI_Setup
  *         Handle the MIDI specific requests
  * @param  pdev: Instance
  * @param  req: USB requests
  * @retval Status
  */
static uint8_t USBD_MIDI_Setup(USBD_HandleTypeDef *pdev, USBD_SetupReqTypedef *req)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDef *)pdev->pClassData;
  uint8_t ret = USBD_OK;

  switch (req->bmRequest & USB_REQ_TYPE_MASK)
  {
    case USB_REQ_TYPE_CLASS:
      /* Handle class-specific requests if needed */
      break;

    case USB_REQ_TYPE_STANDARD:
      switch (req->bRequest)
      {
        case USB_REQ_GET_INTERFACE:
          if (pdev->dev_state == USBD_STATE_CONFIGURED)
          {
            (void)USBD_CtlSendData(pdev, (uint8_t *)&hmidi->alt_setting, 1U);
          }
          else
          {
            USBD_CtlError(pdev, req);
            ret = USBD_FAIL;
          }
          break;

        case USB_REQ_SET_INTERFACE:
          if (pdev->dev_state == USBD_STATE_CONFIGURED)
          {
            hmidi->alt_setting = (uint8_t)(req->wValue);
          }
          else
          {
            USBD_CtlError(pdev, req);
            ret = USBD_FAIL;
          }
          break;

        default:
          USBD_CtlError(pdev, req);
          ret = USBD_FAIL;
          break;
      }
      break;

    default:
      USBD_CtlError(pdev, req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

/**
  * @brief  USBD_MIDI_DataIn
  *         Handle data IN Stage
  * @param  pdev: Device instance
  * @param  epnum: Endpoint number
  * @retval Status
  */
static uint8_t USBD_MIDI_DataIn(USBD_HandleTypeDef *pdev, uint8_t epnum)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDef *)pdev->pClassData;

  if (hmidi != NULL)
  {
    hmidi->tx_state = 0U;
  }

  return (uint8_t)USBD_OK;
}

/**
  * @brief  USBD_MIDI_DataOut
  *         Handle data OUT Stage
  * @param  pdev: Device instance
  * @param  epnum: Endpoint number
  * @retval Status
  */
static uint8_t USBD_MIDI_DataOut(USBD_HandleTypeDef *pdev, uint8_t epnum)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDef *)pdev->pClassData;

  if (hmidi != NULL)
  {
    /* Get the received data length */
    hmidi->rx_length = USBD_LL_GetRxDataSize(pdev, epnum);

    /* Process received MIDI data hier kan je zelf functionaliteit toevoegen */
    /* Voor nu: simpelweg weer klaar maken voor ontvangst */

    /* Prepare endpoint to receive next packet */
    (void)USBD_LL_PrepareReceive(pdev, MIDI_OUT_EP, hmidi->rx_buffer,
                                  MIDI_DATA_OUT_PACKET_SIZE);
  }

  return (uint8_t)USBD_OK;
}

/**
  * @brief  USBD_MIDI_EP0_RxReady
  *         Handle EP0 Rx Ready event
  * @param  pdev: Device handle
  * @retval Status
  */
static uint8_t USBD_MIDI_EP0_RxReady(USBD_HandleTypeDef *pdev)
{
  UNUSED(pdev);
  return (uint8_t)USBD_OK;
}

/**
  * @brief  USBD_MIDI_GetCfgDesc
  *         Return configuration descriptor
  * @param  length: Pointer to data length
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_MIDI_GetCfgDesc(uint16_t *length)
{
  *length = (uint16_t)sizeof(USBD_MIDI_CfgDesc);
  return USBD_MIDI_CfgDesc;
}

/**
  * @brief  USBD_MIDI_GetDeviceQualifierDesc
  *         Return Device Qualifier descriptor
  * @param  length: Pointer to data length
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_MIDI_GetDeviceQualifierDesc(uint16_t *length)
{
  *length = (uint16_t)sizeof(USBD_MIDI_DeviceQualifierDesc);
  return USBD_MIDI_DeviceQualifierDesc;
}

/**
  * @brief  USBD_MIDI_SendData
  *         Send MIDI data on Bulk IN endpoint
  * @param  pdev: Device handle
  * @param  data: Pointer to data buffer
  * @param  length: Data length
  * @retval Status
  */
uint8_t USBD_MIDI_SendData(USBD_HandleTypeDef *pdev, uint8_t *data, uint16_t length)
{
  USBD_MIDI_HandleTypeDef *hmidi = (USBD_MIDI_HandleTypeDef *)pdev->pClassData;

  if (hmidi == NULL)
  {
    return (uint8_t)USBD_FAIL;
  }

  if (hmidi->tx_state == 0U)
  {
    /* Update the packet length */
    hmidi->tx_length = length;

    /* Transmit data */
    hmidi->tx_state = 1U;

    (void)USBD_LL_Transmit(pdev, MIDI_IN_EP, data, length);

    return (uint8_t)USBD_OK;
  }
  else
  {
    return (uint8_t)USBD_BUSY;
  }
}

/**
  * @brief  USBD_MIDI_SendNoteOn
  *         Send MIDI Note ON message
  * @param  pdev: Device handle
  * @param  channel: MIDI channel (0-15)
  * @param  note: MIDI note number (0-127)
  * @param  velocity: Note velocity (0-127)
  * @retval Status
  */
uint8_t USBD_MIDI_SendNoteOn(USBD_HandleTypeDef *pdev, uint8_t channel, 
                              uint8_t note, uint8_t velocity)
{
  uint8_t midi_packet[4];

  /* Construct USB MIDI packet voor Note ON */
  midi_packet[0] = (MIDI_CIN_NOTE_ON << 4) | (channel & 0x0F);  /* Cable 0, CIN = Note ON */
  midi_packet[1] = MIDI_STATUS_NOTE_ON | (channel & 0x0F);      /* Status: Note ON + channel */
  midi_packet[2] = note & 0x7F;                                  /* Note number */
  midi_packet[3] = velocity & 0x7F;                              /* Velocity */

  return USBD_MIDI_SendData(pdev, midi_packet, 4);
}

/**
  * @brief  USBD_MIDI_SendNoteOff
  *         Send MIDI Note OFF message
  * @param  pdev: Device handle
  * @param  channel: MIDI channel (0-15)
  * @param  note: MIDI note number (0-127)
  * @param  velocity: Release velocity (0-127)
  * @retval Status
  */
uint8_t USBD_MIDI_SendNoteOff(USBD_HandleTypeDef *pdev, uint8_t channel, 
                               uint8_t note, uint8_t velocity)
{
  uint8_t midi_packet[4];

  /* Construct USB MIDI packet voor Note OFF */
  midi_packet[0] = (MIDI_CIN_NOTE_OFF << 4) | (channel & 0x0F); /* Cable 0, CIN = Note OFF */
  midi_packet[1] = MIDI_STATUS_NOTE_OFF | (channel & 0x0F);     /* Status: Note OFF + channel */
  midi_packet[2] = note & 0x7F;                                  /* Note number */
  midi_packet[3] = velocity & 0x7F;                              /* Velocity */

  return USBD_MIDI_SendData(pdev, midi_packet, 4);
}

/**
  * @brief  USBD_MIDI_SendControlChange
  *         Send MIDI Control Change message
  * @param  pdev: Device handle
  * @param  channel: MIDI channel (0-15)
  * @param  control: Control number (0-127)
  * @param  value: Control value (0-127)
  * @retval Status
  */
uint8_t USBD_MIDI_SendControlChange(USBD_HandleTypeDef *pdev, uint8_t channel,
                                     uint8_t control, uint8_t value)
{
  uint8_t midi_packet[4];

  /* Construct USB MIDI packet voor Control Change */
  midi_packet[0] = (MIDI_CIN_CONTROL_CHANGE << 4) | (channel & 0x0F);
  midi_packet[1] = MIDI_STATUS_CONTROL_CHANGE | (channel & 0x0F);
  midi_packet[2] = control & 0x7F;
  midi_packet[3] = value & 0x7F;

  return USBD_MIDI_SendData(pdev, midi_packet, 4);
}

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
