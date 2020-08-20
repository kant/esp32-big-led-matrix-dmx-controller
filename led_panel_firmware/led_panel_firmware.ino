#include <stdint.h>
#include <limits.h>
#include <FastLED.h>
#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>


#define NUM_LEDS                                  350

#define ETH_CS_PIN                                5
#define LED_DATA_PIN                              25
#define ETH_RESET_PIN                             26  
#define PERF_MEASUREMENT_PIN                      22        // output used for performance measurement with logic analyzer; will be set, when frame is shown; will be reset approx. 20ms after it has been set

#define RECEIVE_DATA_UDP_PORT                     50000

#define FRAME_PERIOD_TOLERANCE                    5         // if the time to show a frame elapsed for not more than FRAME_PERIOD_TOLERANCE ms, the frame is nevertheless directly displayed


byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xFD
};
IPAddress staticIp(192, 168, 1, 101);
IPAddress myDns(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 0, 0);

//bool useDhcp = false;
bool useDhcp = true;


CRGB leds[NUM_LEDS];


bool receivedInitialMasterTime = false;
bool tookFrameFromRingBuffer = false;


// States for state machine
#define STATE_INITIALIZATION                            0
#define STATE_WAIT_FOR_INITIAL_MASTER_TIME              1
#define STATE_WAIT_FOR_FRAME                            2
#define STATE_WAIT_UNTIL_FRAME_PERIOD_ELAPSED           3

uint8_t currentState = STATE_INITIALIZATION;


uint64_t masterTime = 0;    
uint64_t millisAtMasterTime = 0;
uint64_t estimatedMasterTime = 0;
uint64_t nextFrameMasterTime = UINT64_MAX;

uint64_t lastReceivedFrameMasterTime = UINT64_MAX;


#define PIXEL_DATA_SIZE                                 (NUM_LEDS * 3)
#define FRAME_RING_BUFFER_SIZE                          10

typedef struct {
  bool isEmpty;
  uint64_t timeToPresent;
  uint8_t pixelData[PIXEL_DATA_SIZE];  
} frameRingBufferItem;

frameRingBufferItem frameRingBuffer[FRAME_RING_BUFFER_SIZE];

uint8_t frameRingBufferWriteIndex = 0;


EthernetUDP udp;


uint32_t perfMeasurementPinSetTime = 0;


void setup()
{
  Serial.begin(115200);

  delay(3000);
  Serial.println("bootup...");

  pinMode(PERF_MEASUREMENT_PIN, OUTPUT);
  digitalWrite(PERF_MEASUREMENT_PIN, LOW);

  initFrameRingBuffer();
  
  initFastLed();

  initEthernet();
  
  initUdpListener();
}

void initFrameRingBuffer()
{
  for(int i = 0; i < FRAME_RING_BUFFER_SIZE; ++i)
  {
    frameRingBuffer[i].isEmpty = true;
  }
}

void initFastLed()
{
  FastLED.addLeds<WS2812B, LED_DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(255);
  FastLED.clear();
  FastLED.show();
}

void initEthernet()
{
  Serial.println("Initializing ethernet...");

  Ethernet.init(ETH_CS_PIN);

  bool ethernetConnected = false;
  do
  {
    initEthernetBoard();

    if(useDhcp)
    {
      Serial.println("  Attempting to connect over DHCP...");
      ethernetConnected = Ethernet.begin(mac);
      if(!ethernetConnected)
      {
        if(Ethernet.hardwareStatus() == EthernetNoHardware)
        {
          Serial.println("  Ethernet board not found");
        }
        delay(1000);
      }
    }
    else
    {
      Serial.println("  Connecting with static IP address...");
      Ethernet.begin(mac, staticIp, myDns, gateway, subnet);
      delay(2000);
      if(Ethernet.hardwareStatus() == EthernetNoHardware)
      {
        Serial.println("  Ethernet board not found");
        delay(1000);
      }
      else
      {
        ethernetConnected = true;
      }
    }
  } while(!ethernetConnected);

  Serial.println("  ...successfully connected.");
  Serial.print("  IP address: ");
  Serial.println(Ethernet.localIP());  
}

void initEthernetBoard()
{
  Serial.println("  Initializing ethernet board...");
  
  pinMode(ETH_RESET_PIN, OUTPUT);
  digitalWrite(ETH_RESET_PIN, HIGH);
  delay(250);
  digitalWrite(ETH_RESET_PIN, LOW);
  delay(50);
  digitalWrite(ETH_RESET_PIN, HIGH);
  delay(350);
  
  Serial.println("  ethernet board initialized");
}

void initUdpListener()
{
  Serial.printf("Initializing UDP listener for port...\n", RECEIVE_DATA_UDP_PORT);
  
  bool listenSucceeded = false;
  do
  {
    Serial.printf("  Attempting to listen to port %u ...\n", RECEIVE_DATA_UDP_PORT);
    listenSucceeded = udp.begin(RECEIVE_DATA_UDP_PORT);
    if(!listenSucceeded)
    {
      delay(1000);
    }
  } while(!listenSucceeded);
  Serial.print("  ...successfully listening on IP address: ");
  Serial.println(Ethernet.localIP());

  Serial.println("...UDP listener successfully initialized");
}

void receivedUdpPacket(int packetSize)
{
  if(udp.localPort() == RECEIVE_DATA_UDP_PORT)
  {
    if(packetSize >= 1058)
    {
      // new frame packet
      
// DEBUG
//uint32_t startTime = millis();
      
      processFramePacket();

// DEBUG
//Serial.printf("processing frame packet needed %d ms\n", millis() - startTime);
      
    }
    else
    {
      if(packetSize >= 8)
      {
        // new master time packet

// DEBUG
//uint32_t startTime = millis();
      
        processMasterTimePacket();

// DEBUG
//Serial.printf("processing master time packet needed %d ms\n", millis() - startTime);
        
      }
    }
  }
}

void processFramePacket()
{
// DEBUG
/*
  if(lastReceivedFrameMasterTime != UINT64_MAX)
  {
    uint64_t frameReceptionDiff = estimatedMasterTime - lastReceivedFrameMasterTime;
    if((frameReceptionDiff > 60) || (frameReceptionDiff < 20))
    {
      Serial.printf("### frameReceptionDiff = %llu\n", frameReceptionDiff);
    }
  }
  lastReceivedFrameMasterTime = estimatedMasterTime;
*/

  uint64_t timeToPresent = 0;

  udp.read((uint8_t*)(&timeToPresent), sizeof(timeToPresent));

// DEBUG
//Serial.printf("Received frame with timeToPresent = %llu\n", timeToPresent);
  
  // only consider frames with time to present being in the future
  if(timeToPresent > estimatedMasterTime)  
  {
    addFramePacketToFrameRingBuffer(timeToPresent);
  }
  else
  {
    Serial.println("### skipped frame packet");
    Serial.printf("  timeToPresent = %llu\n", timeToPresent);
    Serial.printf("  estimatedMasterTime = %llu\n", estimatedMasterTime);
  }
}

void addFramePacketToFrameRingBuffer(uint64_t timeToPresent)
{
// DEBUG
if(!frameRingBuffer[frameRingBufferWriteIndex].isEmpty)
{
  Serial.println("### buffer overrun");
}

  frameRingBuffer[frameRingBufferWriteIndex].isEmpty = false;
  frameRingBuffer[frameRingBufferWriteIndex].timeToPresent = timeToPresent;

  udp.read((uint8_t*)(&frameRingBuffer[frameRingBufferWriteIndex].pixelData[0]), 1050);
  
  ++frameRingBufferWriteIndex;
  if(frameRingBufferWriteIndex >= FRAME_RING_BUFFER_SIZE)
  {
    frameRingBufferWriteIndex = 0;
  }
}

void processMasterTimePacket()
{
  uint64_t newMasterTime = 0;
  udp.read((uint8_t*)(&newMasterTime), sizeof(newMasterTime));
  
  millisAtMasterTime = millis();

// DEBUG
/*
Serial.println("Received master time:");
int64_t diff = estimatedMasterTime - newMasterTime;
Serial.printf("  difference between estimated master time and received master time = %lld ms\n", diff);
Serial.printf("  new master time = %llu ms\n", newMasterTime);
*/

  masterTime = newMasterTime;
  receivedInitialMasterTime = true;      

// DEBUG    
/*
Serial.println("Received master time:");
Serial.printf("  %llu / belonging millis() = %u\n", masterTime, millisAtMasterTime);
*/      
}

void getFrameFromRingBuffer()
{
  tookFrameFromRingBuffer = false;
  
  uint8_t indexOfItemWithMinTime = FRAME_RING_BUFFER_SIZE;

  for(int i = 0; i < FRAME_RING_BUFFER_SIZE; ++i)
  {
    if(!frameRingBuffer[i].isEmpty)
    {
      if(frameRingBuffer[i].timeToPresent > estimatedMasterTime)
      {
        if(indexOfItemWithMinTime == FRAME_RING_BUFFER_SIZE)
        {
          indexOfItemWithMinTime = i;
        }
        else
        {
          if(frameRingBuffer[i].timeToPresent < frameRingBuffer[indexOfItemWithMinTime].timeToPresent)
          {
            indexOfItemWithMinTime = i;
          }
        }
      }
      else
      {
        frameRingBuffer[i].isEmpty = true;
      }
    }
  }

  if(indexOfItemWithMinTime != FRAME_RING_BUFFER_SIZE)
  {
    nextFrameMasterTime = frameRingBuffer[indexOfItemWithMinTime].timeToPresent;
    memcpy(&leds[0], &frameRingBuffer[indexOfItemWithMinTime].pixelData[0], 1050);
    frameRingBuffer[indexOfItemWithMinTime].isEmpty = true;
    tookFrameFromRingBuffer = true;
  }
}

void loop()
{
  if(perfMeasurementPinSetTime != 0)
  {
    if((millis() - perfMeasurementPinSetTime) >= 20)
    {
      // reset pin for performance measurement
      digitalWrite(PERF_MEASUREMENT_PIN, LOW);
      perfMeasurementPinSetTime = 0;
    }
  }
  
  int packetSize = udp.parsePacket();
  if(packetSize)
  {
// DEBUG    
//Serial.printf("received udp packet of size %d bytes\n", packetSize);
    
    receivedUdpPacket(packetSize);
  }
  
  // do the following processing all the time
  if(currentState > STATE_WAIT_FOR_INITIAL_MASTER_TIME)
  {
    // estimate master time out of last received master time and millis() since then
    estimatedMasterTime = masterTime + (millis() - millisAtMasterTime);

    if(!tookFrameFromRingBuffer)
    {
      // get frame from ring buffer
      getFrameFromRingBuffer();
    }
        
// DEBUG    
//Serial.printf("estimatedMasterTime = %llu\n", estimatedMasterTime);

  }

  // state machine
  switch(currentState)
  {
    case STATE_INITIALIZATION:
      currentState = STATE_WAIT_FOR_INITIAL_MASTER_TIME;
      Serial.println("waiting for initial master time...");

// DEBUG    
//Serial.println("-> STATE_WAIT_FOR_INITIAL_MASTER_TIME");
      
      break;
    
    case STATE_WAIT_FOR_INITIAL_MASTER_TIME:
      if(receivedInitialMasterTime)
      {
        Serial.printf("received initial master time %llu\n", masterTime);
        Serial.println("waiting for frames...");
        currentState = STATE_WAIT_FOR_FRAME;

// DEBUG    
//Serial.println("-> STATE_WAIT_FOR_FRAME");

      }
      
      break;

    case STATE_WAIT_FOR_FRAME:
      if(tookFrameFromRingBuffer)
      {
        if(nextFrameMasterTime > estimatedMasterTime)
        {
          // time to display next frame is somewhen in future; so wait
          currentState = STATE_WAIT_UNTIL_FRAME_PERIOD_ELAPSED;
      
// DEBUG    
//Serial.println("-> STATE_WAIT_UNTIL_FRAME_PERIOD_ELAPSED");
      
        }
        else
        {
          // time to display next frame alrady elapsed; so skip this frame and wait for the next one
          tookFrameFromRingBuffer = false;
      
          Serial.println("### skipped frame");
          Serial.printf("  estimatedMasterTime = %llu\n", estimatedMasterTime);
          Serial.printf("  nextFrameMasterTime = %llu\n", nextFrameMasterTime);
        }
      }
      break;

    case STATE_WAIT_UNTIL_FRAME_PERIOD_ELAPSED:
      if(nextFrameMasterTime <= estimatedMasterTime)
      {  
        // time elapsed; so show the frame
        showFrame();
        tookFrameFromRingBuffer = false;
        currentState = STATE_WAIT_FOR_FRAME;

// DEBUG    
//Serial.println("-> STATE_WAIT_FOR_FRAME");
    
      }
      break;
  }
}

void showFrame()
{
  FastLED.show();

  // set pin for performance measurement
  perfMeasurementPinSetTime = millis();
  digitalWrite(PERF_MEASUREMENT_PIN, HIGH);
  
// DEBUG    
//Serial.println("frame presented");

}
