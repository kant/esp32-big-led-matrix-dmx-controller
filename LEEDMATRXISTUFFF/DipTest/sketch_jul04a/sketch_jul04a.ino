
uint8_t dipPins[8] = {27, 17, 32, 21, 4, 0, 2, 22};


void setup() {
  Serial.begin(9600);
  setupDipPins();
}

void loop() {
  Serial.println(calculateDMXChannelFromDIPSwitchSettings());
  delay(1000);
}

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

  return returnValue;
}
