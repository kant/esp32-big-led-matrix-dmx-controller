#include <stdint.h>
#include <limits.h>
#include <FastLED.h>
#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>
#include "esp_system.h"
#include "FS.h"
#include "SPIFFS.h"


#define NUM_LEDS                                  350

#define STATUS_LED_PIN                            16
#define FACTORY_DEFAULTS_PIN                      17
#define ETH_CS_PIN                                5
#define LED_DATA_PIN                              25
#define ETH_RESET_PIN                             26  
#define PERF_MEASUREMENT_PIN                      22        // output used for performance measurement with logic analyzer; will be set, when frame is shown; will be reset approx. 20ms after it has been set

#define MAX_DHCP_TRIES                            2         // max count of tries connecting over DHCP before working with static IP

#define RECEIVE_DATA_UDP_PORT                     50000
#define RECEIVE_DATA_UDP_PORT_TPM                 65506
#define TCP_SERVER_PORT                           50001

#define FRAME_PERIOD_TOLERANCE                    5         // if the time to show a frame elapsed for not more than FRAME_PERIOD_TOLERANCE ms, the frame is nevertheless directly displayed


#define NETWORK_SETTINGS_FILENAME                 "/netcfg.bin"
#define FORMAT_SPIFFS_IF_FAILED                   true

#define TCP_CMD_GET_NETWORK_SETTINGS              1
#define TCP_CMD_SET_NETWORK_SETTINGS              2

#define TCP_POSTIVE_ACK                           1
#define TCP_NOT_ENOUGH_DATA_ACK                   2
#define TCP_WRONG_MSG_SIZE_ACK                    3


#pragma pack(1)
typedef struct {
  uint8_t useDhcp;
  uint8_t ipAddress[4];
  uint8_t subnetMask[4];
  uint8_t gateway[4];
  uint8_t dnsServer[4];
} networkSettingsFileContentType;
#pragma pack()

#pragma pack(1)
typedef struct {
  uint8_t useDhcp;
  uint8_t macAddress[6];
  uint8_t ipAddress[4];
  uint8_t subnetMask[4];
  uint8_t gateway[4];
  uint8_t dnsServer[4];
} networkSettingsType;
#pragma pack()

networkSettingsType networkSettings;

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
EthernetUDP udpTpm;
EthernetServer tcpServer(TCP_SERVER_PORT);


uint32_t perfMeasurementPinSetTime = 0;


bool waitingForPowerOffAfterFactoryDefaults = false;
bool ledOffWhileWaitingForPowerOffAfterFactoryDefaults = false;

void setup()
{
  Serial.begin(115200);

  delay(3000);
  Serial.println("bootup...");

  initIo();

  initFrameRingBuffer();
  
  initFastLed();

  initSpiffs();

  readNetworkSettingsFromSpiffs();
  
  initEthernet();
  
  initUdpListener();

  initTcpListener();

  digitalWrite(STATUS_LED_PIN, HIGH);
}

void initIo()
{
  Serial.println("Initializing IO pins...");
  
  pinMode(PERF_MEASUREMENT_PIN, OUTPUT);
  digitalWrite(PERF_MEASUREMENT_PIN, LOW);

  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);

  pinMode(FACTORY_DEFAULTS_PIN, INPUT_PULLUP);
  
  Serial.println("...IO pins successfully initialized");
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

void initSpiffs()
{
  Serial.println("Initializing SPIFFS...");

  bool initSucceeded = false;
  do
  {
    Serial.println("  Attempting to initializing SPIFFS...");
    initSucceeded = SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED);
    if(!initSucceeded)
    {
      delay(1000);
    }
  } while(!initSucceeded);

  Serial.println("...SPIFFS successfully initialized");
}

void readNetworkSettingsFromSpiffs()
{
  Serial.println("Read network settings from SPIFFS...");

  networkSettingsFileContentType networkSettingsFileContent;
  initNetworkSettingsFileContent(networkSettingsFileContent);

  File file = SPIFFS.open(NETWORK_SETTINGS_FILENAME);
  if(!file || file.isDirectory())
  {
    Serial.printf("  could not open file %s\n", NETWORK_SETTINGS_FILENAME);
    Serial.println("  writing default network settings to SPIFFS");
    if(!writeNetworkSettingsToSpiffs(networkSettingsFileContent))
    {
      Serial.println("  failure during writing default network settings");
    }
    copyToNetworkSettings(networkSettingsFileContent);
    Serial.println("...taking default network settings");
  }
  else
  {
    uint32_t file_size = file.size();
    if(file_size != sizeof(networkSettingsFileContent))
    {
      Serial.printf("  file has wrong size (%u bytes)\n", file_size);
      Serial.println("  writing default network settings to SPIFFS");
      if(!writeNetworkSettingsToSpiffs(networkSettingsFileContent))
      {
        Serial.println("  failure during writing default network settings");
      }
      copyToNetworkSettings(networkSettingsFileContent);
      Serial.println("...taking default network settings");
    }
    else
    {
      file.read((uint8_t*)(&networkSettingsFileContent), sizeof(networkSettingsFileContent));
      file.close();
      copyToNetworkSettings(networkSettingsFileContent);
      Serial.println("...network settings successfully read");
    }
  }
}

void initNetworkSettingsFileContent(networkSettingsFileContentType& networkSettingsFileContent)
{
  networkSettingsFileContent = {
    true,                                   // use DHCP (default)
    {192, 168, 1, 101},                     // default IP adress if not DHCP is used
    {255, 255, 255, 0},                     // default subnet mask if not DHCP is used
    {192, 168, 1, 1},                       // default gateway if not DHCP is used
    {192, 168, 1, 1}};                      // default DNS server if not DHCP is used
}

void copyToNetworkSettings(networkSettingsFileContentType& networkSettingsFileContent)
{
  networkSettings.useDhcp = networkSettingsFileContent.useDhcp;
  memcpy(&networkSettings.ipAddress, &networkSettingsFileContent.ipAddress, sizeof(networkSettings.ipAddress));
  memcpy(&networkSettings.subnetMask, &networkSettingsFileContent.subnetMask, sizeof(networkSettings.subnetMask));
  memcpy(&networkSettings.gateway, &networkSettingsFileContent.gateway, sizeof(networkSettings.gateway));
  memcpy(&networkSettings.dnsServer, &networkSettingsFileContent.dnsServer, sizeof(networkSettings.dnsServer));
}

bool writeNetworkSettingsToSpiffs(networkSettingsFileContentType& networkSettingsFileContent)
{
  File file = SPIFFS.open(NETWORK_SETTINGS_FILENAME, FILE_WRITE);
  if(!file || file.isDirectory())
  {
    return false;
  }
  else
  {
    file.write((uint8_t*)(&networkSettingsFileContent), sizeof(networkSettingsFileContent));
    file.flush();
    file.close();
  }
  return true;
}

void initEthernet()
{
  Serial.println("Initializing ethernet...");

  esp_read_mac(networkSettings.macAddress, ESP_MAC_WIFI_STA);
  Serial.printf("  Took MAC address from ESP32 WiFi for the ethernet interface: %s\n", macToStr(networkSettings.macAddress).c_str());

  Ethernet.init(ETH_CS_PIN);

  bool ethernetConnected = false;
  uint8_t dhcpTries = 0;
  do
  {
    initEthernetBoard();

    if((networkSettings.useDhcp) && (dhcpTries < MAX_DHCP_TRIES))
    {
      Serial.println("  Attempting to connect over DHCP...");
      ethernetConnected = Ethernet.begin(networkSettings.macAddress);
      if(!ethernetConnected)
      {
        if(Ethernet.hardwareStatus() == EthernetNoHardware)
        {
          Serial.println("  Ethernet board not found");
        }
        else
        {
          ++dhcpTries;
        }
        delay(1000);
      }
    }
    if((!networkSettings.useDhcp) || (dhcpTries >= MAX_DHCP_TRIES))
    {
      Serial.println("  Connecting with static IP address...");
      IPAddress ipAddress = IPAddress(networkSettings.ipAddress);
      IPAddress subnetMask = IPAddress(networkSettings.subnetMask);
      IPAddress gateway = IPAddress(networkSettings.gateway);
      IPAddress dnsServer = IPAddress(networkSettings.dnsServer);
      Serial.printf("    IP address = %s\n", ipAddress.toString().c_str());
      Serial.printf("    subnet mask = %s\n", subnetMask.toString().c_str());
      Serial.printf("    gateway = %s\n", gateway.toString().c_str());
      Serial.printf("    DNS server = %s\n", dnsServer.toString().c_str());
      Ethernet.begin(networkSettings.macAddress, ipAddress, dnsServer, gateway, subnetMask);
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

  Serial.println("...ethernet successfully initialized");
}

String macToStr(uint8_t* macAddressBytes)
{
  char baseMacChr[18] = {0};
  sprintf(baseMacChr, "%02X:%02X:%02X:%02X:%02X:%02X", macAddressBytes[0], macAddressBytes[1], macAddressBytes[2], macAddressBytes[3], macAddressBytes[4], macAddressBytes[5]);
  return String(baseMacChr);
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
  initUdpPortListener(udp, RECEIVE_DATA_UDP_PORT);
  initUdpPortListener(udpTpm, RECEIVE_DATA_UDP_PORT_TPM);
}

void initUdpPortListener(EthernetUDP& udp, uint16_t udpPort)
{
  Serial.printf("Initializing UDP listener for port...\n", udpPort);
  
  bool listenSucceeded = false;
  do
  {
    Serial.printf("  Attempting to listen to port %u ...\n", udpPort);
    listenSucceeded = udp.begin(udpPort);
    if(!listenSucceeded)
    {
      delay(1000);
    }
  } while(!listenSucceeded);
  Serial.print("  ...successfully listening on IP address: ");
  Serial.println(Ethernet.localIP());

  Serial.println("...UDP listener successfully initialized");
}

void initTcpListener()
{
  Serial.printf("Listen to TCP connections on port %u ...\n", TCP_SERVER_PORT);

  tcpServer.begin();
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

void receivedUdpTpmPacket(int packetSize)
{
  if(udpTpm.localPort() == RECEIVE_DATA_UDP_PORT_TPM)
  {
    if(packetSize >= 1057)
    {
      // new frame packet
      processTpmFramePacket();
    }
  }
}

void processTpmFramePacket()
{
  uint8_t header[6];
  udpTpm.read(&header[0], 6);

  udpTpm.read((uint8_t*)(&leds[0]), PIXEL_DATA_SIZE);

  uint8_t endByte;
  udpTpm.read(&endByte, 1);

  showFrame();
}


void loop()
{
  if(waitingForPowerOffAfterFactoryDefaults)
  {
    if(ledOffWhileWaitingForPowerOffAfterFactoryDefaults)
    {
      digitalWrite(STATUS_LED_PIN, LOW);
    }
    else
    {
      digitalWrite(STATUS_LED_PIN, HIGH);
    }
    ledOffWhileWaitingForPowerOffAfterFactoryDefaults = !ledOffWhileWaitingForPowerOffAfterFactoryDefaults;
    sleep(200);
    return;
  }
  if(digitalRead(FACTORY_DEFAULTS_PIN) == LOW)
  {
    factoryDefaults();
    return;  
  }
  
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

  packetSize = udpTpm.parsePacket();
  if(packetSize)
  {
// DEBUG    
//Serial.printf("received udp TPM2 packet of size %d bytes\n", packetSize);
    
    receivedUdpTpmPacket(packetSize);
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

  processTcp();
}

void factoryDefaults()
{
  Serial.println("Writing factory defaults...");

  networkSettingsFileContentType networkSettingsFileContent;
  initNetworkSettingsFileContent(networkSettingsFileContent);

  if(!writeNetworkSettingsToSpiffs(networkSettingsFileContent))
  {
    Serial.println("  failure during writing default network settings");
  }

  waitingForPowerOffAfterFactoryDefaults = true;
  
  Serial.println("...Factory defaults have been written - please power off and on again");
}

void processTcp()
{
  EthernetClient tcpClient = tcpServer.available();
  if(tcpClient)
  {
    
// DEBUG
//Serial.printf("TCP client %s connected\n", tcpClient.remoteIP().toString().c_str());

    uint8_t cmd = tcpClient.read();
    processTcpCmd(tcpClient, cmd);
    
    tcpClient.stop();
  }
}

void processTcpCmd(EthernetClient& tcpClient, uint8_t cmd)
{
  if(cmd == TCP_CMD_GET_NETWORK_SETTINGS)
  {

// DEBUG
//Serial.println("sending network settings");

    sendNetworkSettings(tcpClient);
  }
  else if(cmd == TCP_CMD_SET_NETWORK_SETTINGS)
  {

// DEBUG
//Serial.println("receiving network settings");

    receiveNetworkSettings(tcpClient);
  }
}

void sendNetworkSettings(EthernetClient& tcpClient)
{
  // send back the current network settings inside the answer to the client command
  tcpClient.write(sizeof(networkSettings)); // size of the network settings data
  tcpClient.write((uint8_t*)(&networkSettings), sizeof(networkSettings)); // network settings data
  tcpClient.flush();
}

void receiveNetworkSettings(EthernetClient& tcpClient)
{
  // receive new network settings
  int messageSize = tcpClient.read(); // size of the new network settings data

// DEBUG
//Serial.printf("messageSize = %d\n", messageSize);
  
  if(messageSize == sizeof(networkSettingsFileContentType))
  {
    uint8_t receivedMessage[sizeof(networkSettingsFileContentType)];
    if(receiveNetworkSettingsData(tcpClient, &receivedMessage[0]))
    {
      // send back a positive acknowledgement inside the answer to the client command
      tcpClient.write(TCP_POSTIVE_ACK);
      tcpClient.flush();

      networkSettingsFileContentType receivedNetworkSettings;
      memcpy(&receivedNetworkSettings, &receivedMessage[0], sizeof(receivedNetworkSettings));
      
      dumpReceivedNetworkSettings(receivedNetworkSettings);
      
      if(!writeNetworkSettingsToSpiffs(receivedNetworkSettings))
      {
        Serial.println("### failure during writing new network settings into SPIFFS");
      }

      tcpClient.stop();
      
      Serial.println("################################### restarting... ###################################");
      delay(1000);
      ESP.restart();
    }
    else
    {
      // send back a negative acknowledgement inside the answer to the client command
      tcpClient.write(TCP_NOT_ENOUGH_DATA_ACK);
      tcpClient.flush();
      
      Serial.println("### command <set network settings> does not contain enough data");  
    }
  }
  else
  {
    // send back a negative acknowledgement inside the answer to the client command
    tcpClient.write(TCP_WRONG_MSG_SIZE_ACK);
    tcpClient.flush();
    
    Serial.println("### command <set network settings> is followed by wrong message size");  
  }
}

bool receiveNetworkSettingsData(EthernetClient& tcpClient, uint8_t* receivedMessage)
{
  uint8_t totalBytesRead = 0;
  bool noDataAvailable = false;
  
  while((totalBytesRead < sizeof(networkSettingsFileContentType)) && (!noDataAvailable))
  {
    int byteRead = tcpClient.read();
    
// DEBUG
//Serial.printf("byteRead = %d\n", byteRead);

    if(byteRead >= 0)
    {
      receivedMessage[totalBytesRead] = byteRead;
      ++totalBytesRead;
    }
    else
    {
      noDataAvailable = true;
    }
  }
  
  return !noDataAvailable;
}

void dumpReceivedNetworkSettings(networkSettingsFileContentType& receivedNetworkSettings)
{
  IPAddress ipAddress = IPAddress(receivedNetworkSettings.ipAddress);
  IPAddress subnetMask = IPAddress(receivedNetworkSettings.subnetMask);
  IPAddress gateway = IPAddress(receivedNetworkSettings.gateway);
  IPAddress dnsServer = IPAddress(receivedNetworkSettings.dnsServer);
  Serial.println("received new network settings:");
  Serial.printf("  useDhcp = %u\n", receivedNetworkSettings.useDhcp);
  Serial.printf("  IP address = %s\n", ipAddress.toString().c_str());
  Serial.printf("  subnet mask = %s\n", subnetMask.toString().c_str());
  Serial.printf("  gateway = %s\n", gateway.toString().c_str());
  Serial.printf("  DNS server = %s\n", dnsServer.toString().c_str());
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
