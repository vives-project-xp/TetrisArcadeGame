/**
  ******************************************************************************
  * @file    usbd_desc.c
  * @brief   USB Device Descriptor implementation
  * @author  Project Experience 2.2
  * @date    2026
  ******************************************************************************
  * @attention
  *
  * Deze file bevat de USB Device Descriptors voor het MIDI device:
  * - Device Descriptor: Identificeert het device (VID, PID, versies)
  * - String Descriptors: Product naam, manufacturer, serial number
  * - Language Descriptor: Ondersteunde talen
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "usbd_core.h"
#include "usbd_desc.h"
#include "usbd_conf.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/

/* USB Standard Device Descriptor */
__ALIGN_BEGIN uint8_t USBD_FS_DeviceDesc[USB_LEN_DEV_DESC] __ALIGN_END =
{
  0x12,                       /* bLength */
  USB_DESC_TYPE_DEVICE,       /* bDescriptorType */
  0x00, 0x02,                 /* bcdUSB: USB 2.0 */
  0x00,                       /* bDeviceClass: Defined in Interface Descriptor */
  0x00,                       /* bDeviceSubClass */
  0x00,                       /* bDeviceProtocol */
  USB_MAX_EP0_SIZE,           /* bMaxPacketSize0 */
  LOBYTE(USBD_VID),           /* idVendor */
  HIBYTE(USBD_VID),
  LOBYTE(USBD_PID_FS),        /* idProduct */
  HIBYTE(USBD_PID_FS),
  0x00, 0x02,                 /* bcdDevice: Device release 2.00 */
  USBD_IDX_MFC_STR,           /* iManufacturer: Index of manufacturer string */
  USBD_IDX_PRODUCT_STR,       /* iProduct: Index of product string */
  USBD_IDX_SERIAL_STR,        /* iSerialNumber: Index of serial number string */
  USBD_MAX_NUM_CONFIGURATION  /* bNumConfigurations */
};

/* USB Standard String Descriptors */
__ALIGN_BEGIN uint8_t USBD_LangIDDesc[USB_LEN_LANGID_STR_DESC] __ALIGN_END =
{
  USB_LEN_LANGID_STR_DESC,
  USB_DESC_TYPE_STRING,
  LOBYTE(USBD_LANGID_STRING),
  HIBYTE(USBD_LANGID_STRING)
};

/* Internal string descriptor */
__ALIGN_BEGIN uint8_t USBD_StrDesc[USBD_MAX_STR_DESC_SIZ] __ALIGN_END;

/* Private function prototypes -----------------------------------------------*/
static uint8_t *USBD_FS_DeviceDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_LangIDStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_ManufacturerStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_ProductStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_SerialStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_ConfigStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);
static uint8_t *USBD_FS_InterfaceStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length);

/**
  * @brief  USB Device Descriptors Structure
  */
USBD_DescriptorsTypeDef FS_Desc =
{
  USBD_FS_DeviceDescriptor,
  USBD_FS_LangIDStrDescriptor,
  USBD_FS_ManufacturerStrDescriptor,
  USBD_FS_ProductStrDescriptor,
  USBD_FS_SerialStrDescriptor,
  USBD_FS_ConfigStrDescriptor,
  USBD_FS_InterfaceStrDescriptor
};

/* Private functions ---------------------------------------------------------*/

/**
  * @brief  Return the device descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_DeviceDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  *length = sizeof(USBD_FS_DeviceDesc);
  return USBD_FS_DeviceDesc;
}

/**
  * @brief  Return the Language ID string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_LangIDStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  *length = sizeof(USBD_LangIDDesc);
  return USBD_LangIDDesc;
}

/**
  * @brief  Return the product string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_ProductStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  USBD_GetString((uint8_t *)USBD_PRODUCT_STRING_FS, USBD_StrDesc, length);
  return USBD_StrDesc;
}

/**
  * @brief  Return the manufacturer string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_ManufacturerStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  USBD_GetString((uint8_t *)USBD_MANUFACTURER_STRING, USBD_StrDesc, length);
  return USBD_StrDesc;
}

/**
  * @brief  Return the serial number string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_SerialStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  
  /* Generate unique serial number from device UID */
  uint32_t deviceserial0, deviceserial1, deviceserial2;
  
  deviceserial0 = *(uint32_t *)DEVICE_ID1;
  deviceserial1 = *(uint32_t *)DEVICE_ID2;
  deviceserial2 = *(uint32_t *)DEVICE_ID3;
  
  deviceserial0 += deviceserial2;
  
  /* Format serial number as hex string */
  USBD_StrDesc[0] = USB_SIZ_STRING_SERIAL;
  USBD_StrDesc[1] = USB_DESC_TYPE_STRING;
  
  /* Convert to Unicode string */
  uint8_t idx = 2;
  uint32_t val = deviceserial0;
  
  for (int i = 0; i < 8; i++)
  {
    uint8_t digit = (val >> 28) & 0x0F;
    USBD_StrDesc[idx++] = (digit < 10) ? ('0' + digit) : ('A' + digit - 10);
    USBD_StrDesc[idx++] = 0;
    val <<= 4;
  }
  
  val = deviceserial1;
  for (int i = 0; i < 8; i++)
  {
    uint8_t digit = (val >> 28) & 0x0F;
    USBD_StrDesc[idx++] = (digit < 10) ? ('0' + digit) : ('A' + digit - 10);
    USBD_StrDesc[idx++] = 0;
    val <<= 4;
  }
  
  *length = USB_SIZ_STRING_SERIAL;
  return USBD_StrDesc;
}

/**
  * @brief  Return the configuration string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_ConfigStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  USBD_GetString((uint8_t *)USBD_CONFIGURATION_STRING_FS, USBD_StrDesc, length);
  return USBD_StrDesc;
}

/**
  * @brief  Return the interface string descriptor
  * @param  speed: Current device speed
  * @param  length: Pointer to data length variable
  * @retval Pointer to descriptor buffer
  */
static uint8_t *USBD_FS_InterfaceStrDescriptor(USBD_SpeedTypeDef speed, uint16_t *length)
{
  UNUSED(speed);
  USBD_GetString((uint8_t *)USBD_INTERFACE_STRING_FS, USBD_StrDesc, length);
  return USBD_StrDesc;
}

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
