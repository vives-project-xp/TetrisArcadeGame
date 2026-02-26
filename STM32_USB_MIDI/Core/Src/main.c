/**
  ******************************************************************************
  * @file    main.c
  * @brief   USB MIDI Device Main Application voor STM32H533RE
  * @author  Project Experience 2.2
  * @date    2026
  ******************************************************************************
  * @attention
  *
  * Dit is de hoofdapplicatie voor het USB MIDI device project.
  * 
  * Functionaliteit:
  * - Initialiseert de STM32H533RE hardware (clocks, GPIO, USB)
  * - Configureert USB als MIDI device
  * - Detecteert User Button press en stuurt MIDI Note ON/OFF messages
  * - Blinkt LED bij MIDI activiteit
  *
  * Hardware:
  * - User Button: PC13 (blauw, active LOW met pull-up)
  * - LED: PA5 (groen, active HIGH)
  * - USB: PA11 (USB_DM), PA12 (USB_DP)
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usbd_core.h"
#include "usbd_desc.h"
#include "usbd_midi.h"

/* Private includes ----------------------------------------------------------*/
/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
#define BUTTON_PIN GPIO_PIN_13
#define BUTTON_PORT GPIOC
#define LED_PIN GPIO_PIN_5
#define LED_PORT GPIOA

/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
USBD_HandleTypeDef hUsbDeviceFS;

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USB_DEVICE_Init(void);
void Error_Handler(void);

/* Private user code ---------------------------------------------------------*/

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* MCU Configuration--------------------------------------------------------*/
  
  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();

  /* Variables voor button debouncing */
  uint8_t button_state = 1;          /* 1 = niet ingedrukt (pull-up) */
  uint8_t last_button_state = 1;
  uint32_t last_debounce_time = 0;
  uint32_t debounce_delay = 50;      /* 50ms debounce tijd */
  uint8_t note_playing = 0;          /* Track of note aan staat */

  /* Infinite loop */
  while (1)
  {
    /* Lees button state */
    uint8_t reading = HAL_GPIO_ReadPin(BUTTON_PORT, BUTTON_PIN);

    /* Check of button state veranderd is */
    if (reading != last_button_state)
    {
      /* Reset debounce timer */
      last_debounce_time = HAL_GetTick();
    }

    /* Check of debounce tijd voorbij is */
    if ((HAL_GetTick() - last_debounce_time) > debounce_delay)
    {
      /* Als button state stabiel veranderd is */
      if (reading != button_state)
      {
        button_state = reading;

        /* Button ingedrukt (active LOW) */
        if (button_state == 0)
        {
          /* Stuur MIDI Note ON */
          USBD_MIDI_SendNoteOn(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MAX);
          note_playing = 1;
          
          /* Turn LED ON */
          HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);
        }
        /* Button losgelaten */
        else
        {
          /* Stuur MIDI Note OFF */
          if (note_playing)
          {
            USBD_MIDI_SendNoteOff(&hUsbDeviceFS, 0, MIDI_NOTE_C4, MIDI_VELOCITY_MED);
            note_playing = 0;
          }
          
          /* Turn LED OFF */
          HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);
        }
      }
    }

    last_button_state = reading;

    /* Kleine delay om CPU niet volledig te belasten */
    HAL_Delay(1);
  }
}

/**
  * @brief System Clock Configuration
  * 
  * Configureert de system clock voor USB (48 MHz vereist)
  * 
  * Clock Tree voor H533RE met USB:
  * - HSE: 8 MHz (externe crystal op Nucleo)
  * - PLL1: SYSCLK = 250 MHz
  * - PLL3: USB Clock = 48 MHz (exact vereist voor USB Full-Speed)
  * 
  * @note Deze functie moet aangepast worden op basis van je 
  *       STM32CubeMX clock configuratie
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE0);

  while (!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}

  /** Initializes the RCC Oscillators according to the specified parameters
   * in the RCC_OscInitTypeDef structure.
   */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI48 | RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_BYPASS;              /* ST-Link MCO geeft 8 MHz */
  RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;              /* 48 MHz voor USB */
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLL1_SOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 2;                           /* 8 MHz / 2 = 4 MHz */
  RCC_OscInitStruct.PLL.PLLN = 125;                         /* 4 MHz * 125 = 500 MHz */
  RCC_OscInitStruct.PLL.PLLP = 2;                           /* 500 MHz / 2 = 250 MHz (SYSCLK) */
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  RCC_OscInitStruct.PLL.PLLRGE = RCC_PLL1_VCIRANGE_1;
  RCC_OscInitStruct.PLL.PLLVCOSEL = RCC_PLL1_VCORANGE_WIDE;
  RCC_OscInitStruct.PLL.PLLFRACN = 0;
  
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                              | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2
                              | RCC_CLOCKTYPE_PCLK3;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;        /* 250 MHz */
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;         /* 250 MHz */
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;         /* 250 MHz */
  RCC_ClkInitStruct.APB3CLKDivider = RCC_HCLK_DIV1;         /* 250 MHz */

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure the USB clock source */
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;  /* 48 MHz voor USB */
  
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief GPIO Initialization Function
  * 
  * Configureert:
  * - PC13: User Button (input, pull-up)
  * - PA5: LED (output, push-pull)
  * - PA11, PA12: USB (automatisch geconfigureerd door USB HAL)
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();

  /* Configure GPIO pin Output Level voor LED */
  HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);

  /* Configure User Button Pin (PC13) */
  GPIO_InitStruct.Pin = BUTTON_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;                       /* Internal pull-up */
  HAL_GPIO_Init(BUTTON_PORT, &GPIO_InitStruct);

  /* Configure LED Pin (PA5) */
  GPIO_InitStruct.Pin = LED_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_PORT, &GPIO_InitStruct);
}

/**
  * @brief  USB Device Initialization
  * 
  * Initialiseert de USB Device middleware met MIDI class
  */
static void MX_USB_DEVICE_Init(void)
{
  /* Init Device Library, add supported class and start the library. */
  if (USBD_Init(&hUsbDeviceFS, &FS_Desc, DEVICE_FS) != USBD_OK)
  {
    Error_Handler();
  }
  
  if (USBD_RegisterClass(&hUsbDeviceFS, &USBD_MIDI) != USBD_OK)
  {
    Error_Handler();
  }
  
  if (USBD_Start(&hUsbDeviceFS) != USBD_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  
  /* Blink LED snel om error aan te geven */
  while (1)
  {
    HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
    HAL_Delay(100);
  }
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
