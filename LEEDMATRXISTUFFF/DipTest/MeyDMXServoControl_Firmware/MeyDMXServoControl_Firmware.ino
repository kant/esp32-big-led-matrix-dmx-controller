#include <DMXSerial.h>

#define STATUS_LED_PIN    10  // PB2
#define SERVO_PIN         2   // PD2 / ATmega328 Pin 4

// DMX address can be set by a 8 bit DIP Switch (correspondig inputs get LOW, when DIP switch is set!)
// see https://playground.arduino.cc/Learning/Pins for an overview of pin numbers and ports
#define DMX_ADR_DIP_SW_1  5   // PD5 / ATmega328 Pin 11
#define DMX_ADR_DIP_SW_2  6   // PD6 / ATmega328 Pin 12
#define DMX_ADR_DIP_SW_3  7   // PD7 / ATmega328 Pin 13
#define DMX_ADR_DIP_SW_4  8   // PB0 / ATmega328 Pin 14
#define DMX_ADR_DIP_SW_5  9   // PB1 / ATmega328 Pin 15
#define DMX_ADR_DIP_SW_6  4   // PD4 / ATmega328 Pin 6
#define DMX_ADR_DIP_SW_7  3   // PD3 / ATmega328 Pin 5
#define DMX_ADR_DIP_SW_8  15  // PC1 / ATmega328 Pin 24

#define STATUS_LED_BLINK_NORMAL_MICROSECONDS  1000000 // 1000 ms
#define STATUS_LED_BLINK_ERROR_MICROSECONDS   250000  // 250 ms

#define SERVO_PWM_PERIOD_MICROSECONDS              20000 // 20 ms
#define SERVO_PWM_DUTY_CYCLE_MIN_MICROSECONDS      762   // 0.762 ms
#define SERVO_PWM_DUTY_CYCLE_MAX_MICROSECONDS      1525  // 1.525 ms

#define INTERRUPT_CYCLE_MICROSECONDS  40 // 40µs

#define STATUS_LED_BLINK_NORMAL_INTERRUPT_CYCLES_COUNT      (STATUS_LED_BLINK_NORMAL_MICROSECONDS / INTERRUPT_CYCLE_MICROSECONDS)
#define STATUS_LED_BLINK_ERROR_INTERRUPT_CYCLES_COUNT       (STATUS_LED_BLINK_ERROR_MICROSECONDS / INTERRUPT_CYCLE_MICROSECONDS)

#define SERVO_PWM_PERIOD_INTERRUPT_CYCLES_COUNT             (SERVO_PWM_PERIOD_MICROSECONDS / INTERRUPT_CYCLE_MICROSECONDS)
#define SERVO_PWM_DUTY_CYCLE_MIN_INTERRUPT_CYCLES_COUNT     (SERVO_PWM_DUTY_CYCLE_MIN_MICROSECONDS / INTERRUPT_CYCLE_MICROSECONDS)
#define SERVO_PWM_DUTY_CYCLE_MAX_INTERRUPT_CYCLES_COUNT     (SERVO_PWM_DUTY_CYCLE_MAX_MICROSECONDS / INTERRUPT_CYCLE_MICROSECONDS)

static uint8_t dmxChannelServo = 0; // will be calculated at runtime out of DIP switch settings; address range: 0..255
static uint8_t dmxServoChannelValue = 0;

static void setupPins();
static uint8_t calculateDMXChannelFromDIPSwitchSettings();

static uint32_t statusLEDBlinkCounter = 0;
static bool statusLEDIsOn = false;
static bool inErrorState = true;

static uint16_t servoPWMStepCounter = 0;
static uint16_t servoPWMPulseSteps = SERVO_PWM_DUTY_CYCLE_MIN_INTERRUPT_CYCLES_COUNT;
static bool servoPWMPulseActive = true;

static bool incrementPos = true;

void setup()
{
  setupPins();

  DMXSerial.init(DMXReceiver);

  noInterrupts();
  TCCR1A = 0x00;
  TCCR1B = 0x09;
  TCNT1 = 0;
  OCR1A = 320; // 8 MHz --> 0.000000125 s; interrupt every 40 µs --> 0.00004 s / 0.000000125 s = 320
  TIMSK1 |= (1 << OCIE1A);
  interrupts();
}

ISR(TIMER1_COMPA_vect) // is triggered every 40 µs
{
  ++servoPWMStepCounter;
  if (servoPWMStepCounter >= SERVO_PWM_PERIOD_INTERRUPT_CYCLES_COUNT)
  {
    // new PWM cycle
    servoPWMStepCounter = 0;

    // calculate PWM pulse cycle count
    servoPWMPulseSteps = SERVO_PWM_DUTY_CYCLE_MIN_INTERRUPT_CYCLES_COUNT + 
                         (((SERVO_PWM_DUTY_CYCLE_MAX_INTERRUPT_CYCLES_COUNT - SERVO_PWM_DUTY_CYCLE_MIN_INTERRUPT_CYCLES_COUNT) * (uint16_t)dmxServoChannelValue) / 255);
    // start PWM pulse
    digitalWrite(SERVO_PIN, HIGH);
    servoPWMPulseActive = true;
  }
  else if ((servoPWMPulseActive == true) && (servoPWMStepCounter >= servoPWMPulseSteps))
  {
    // stop PWM pulse
    digitalWrite(SERVO_PIN, LOW);
    servoPWMPulseActive = false;
  }
  
  ++statusLEDBlinkCounter;
  uint16_t statusLEDBlinkCounterMax = STATUS_LED_BLINK_NORMAL_INTERRUPT_CYCLES_COUNT;
  if (inErrorState == true)
  {
    statusLEDBlinkCounterMax = STATUS_LED_BLINK_ERROR_INTERRUPT_CYCLES_COUNT;
  }
  if (statusLEDBlinkCounter >= statusLEDBlinkCounterMax)
  {
    statusLEDBlinkCounter = 0;
    if (statusLEDIsOn == true)
    {
      digitalWrite(STATUS_LED_PIN, LOW);
    }
    else
    {
      digitalWrite(STATUS_LED_PIN, HIGH);
    }
    statusLEDIsOn = !statusLEDIsOn;
  }

}

void loop()
{
  unsigned long timeSincelastDMXPacketHasBeenReceived = DMXSerial.noDataSince();

  calculateDMXChannelFromDIPSwitchSettings();
  
// DEBUG: use fixed DMX address 1 for Servo
// dmxChannelServo = 1;

  if (timeSincelastDMXPacketHasBeenReceived < 1000)
  {
    inErrorState = false;
    if (dmxChannelServo > 0)
    {
      dmxServoChannelValue = DMXSerial.read(dmxChannelServo);
    }
  }
  else
  {
    inErrorState = true;

    digitalWrite(SERVO_PIN, LOW);
  }

// DEBUG: move Servo periodically between min and max angle
/*
  if (incrementPos == true)
  {
    dmxServoChannelValue = dmxServoChannelValue + 1;
    if (dmxServoChannelValue == 255)
    {
      incrementPos = false;
    }
  }
  else
  {
    dmxServoChannelValue = dmxServoChannelValue - 1;
    if (dmxServoChannelValue == 0)
    {
      incrementPos = true;
    }
  }

  delay(5);
*/
}


static void setupPins()
{
  pinMode(SERVO_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(DMX_ADR_DIP_SW_1, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_2, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_3, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_4, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_5, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_6, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_7, INPUT_PULLUP);
  pinMode(DMX_ADR_DIP_SW_8, INPUT_PULLUP);
}

static uint8_t calculateDMXChannelFromDIPSwitchSettings()
{
  dmxChannelServo = 0;
  if (digitalRead(DMX_ADR_DIP_SW_1) == 0)
  {
    dmxChannelServo += 1;
  }
  if (digitalRead(DMX_ADR_DIP_SW_2) == 0)
  {
    dmxChannelServo += 2;
  }
  if (digitalRead(DMX_ADR_DIP_SW_3) == 0)
  {
    dmxChannelServo += 4;
  }
  if (digitalRead(DMX_ADR_DIP_SW_4) == 0)
  {
    dmxChannelServo += 8;
  }
  if (digitalRead(DMX_ADR_DIP_SW_5) == 0)
  {
    dmxChannelServo += 16;
  }
  if (digitalRead(DMX_ADR_DIP_SW_6) == 0)
  {
    dmxChannelServo += 32;
  }
  if (digitalRead(DMX_ADR_DIP_SW_7) == 0)
  {
    dmxChannelServo += 64;
  }
  if (digitalRead(DMX_ADR_DIP_SW_8) == 0)
  {
    dmxChannelServo += 128;
  }
}




uint8_t dipPins[8] = {5, 6, 7, 8, 9, 4, 3, 15};

static void setupDipPins()
{
  for(uint8_t i=0; i < 8; ++i)
    pinMode(dipPins[i], INPUT_PULLUP);
}

static uint8_t calculateDMXChannelFromDIPSwitchSettings()
{
  uint8_t returnValue = 0;

  for(uint8_t i=0; i < 8; ++i)
    returnValue += (!digitalRead(dipPins[i]) << i);

/*  
  for(uint8_t i=0; i < 8; ++i)
  {
    uint8_t invertedPinStatus = !digitalRead(dipPins[i])
    
    // entweder:  
    if(invertedPinStatus == 1)
      returnValue += 2^i;
    // oder:
    if(invertedPinStatus == 1)
      returnValue += (1 << i)
    // oder:
    returnValue += (invertedPinStatus << i)
  }
*/
  return returnValue;
}
