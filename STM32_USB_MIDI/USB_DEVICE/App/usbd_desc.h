/**
  ******************************************************************************
  * @file    usbd_desc.h
  * @brief   Header file for USB Device Descriptors
  ******************************************************************************
  */

#ifndef __USBD_DESC_H
#define __USBD_DESC_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "usbd_def.h"

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
#define DEVICE_ID1                      (UID_BASE)
#define DEVICE_ID2                      (UID_BASE + 0x4)
#define DEVICE_ID3                      (UID_BASE + 0x8)

#define USB_SIZ_STRING_SERIAL           0x1A

/* USB Device Descriptor parameters */
#define USBD_VID                        0x0483      /* STMicroelectronics */
#define USBD_PID_FS                     0x5740      /* USB MIDI Device */
#define USBD_LANGID_STRING              1033        /* English (US) */
#define USBD_MANUFACTURER_STRING        "STMicroelectronics"
#define USBD_PRODUCT_STRING_FS          "STM32 MIDI Device"
#define USBD_CONFIGURATION_STRING_FS    "MIDI Config"
#define USBD_INTERFACE_STRING_FS        "MIDI Interface"

/* Exported macro ------------------------------------------------------------*/
/* Exported variables --------------------------------------------------------*/
extern USBD_DescriptorsTypeDef FS_Desc;

/* Exported functions --------------------------------------------------------*/

#ifdef __cplusplus
}
#endif

#endif /* __USBD_DESC_H */
