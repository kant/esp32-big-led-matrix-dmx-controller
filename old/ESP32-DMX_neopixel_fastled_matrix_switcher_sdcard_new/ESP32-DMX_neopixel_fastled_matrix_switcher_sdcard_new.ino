#include <dmx.h>
#include <FastLED.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"


#define MATRIX_PIN 25
#define NUM_LEDS 1400

//Channelstates: 
bool channelstate1_old = false;
bool channelstate2_old = false;
bool channelstate3_old = false;
bool channelstate4_old = false;
bool channelstate5_old = false;
bool channelstate6_old = false;
bool channelstate7_old = false;
bool channelstate8_old = false;
bool channelstate9_old = false;
bool channelstate10_old = false;

uint8_t dipPins[8] = {27, 17, 32, 21, 4, 0, 2, 22};
int dipChannelValue;
int r;
int g;
int g1;
int b;
int b1;
int file_data[4200];
int frame0_data[4200];
int frame1_data[4200];
int frame2_data[4200];
int value;
bool channelstate;
bool channelstate_old = false;
int channel;
int const btn = 2;
String modus;

CRGB leds[NUM_LEDS];

int getRgbValues(String fader) {
  File file = SD.open(fader);
  Serial.println("Go");
  int i = 0;
  while(file.available())
  { 
    file_data[i] = file.read();
    i = i + 1;
  }
  return file_data[4200];
  file.close();
}
int frame0getRgbValues(String fader) {
  File file = SD.open(fader);
  Serial.println("Go");
  int i = 0;
  while(file.available())
  { 
    frame0_data[i] = file.read();
    i = i + 1;
  }
  return frame0_data[4200];
  file.close();
}
int frame1getRgbValues(String fader) {
  File file = SD.open(fader);
  Serial.println("Go");
  int i = 0;
  while(file.available())
  { 
    frame1_data[i] = file.read();
    i = i + 1;
  }
  return frame1_data[4200];
  file.close();
}
int frame2getRgbValues(String fader) {
  File file = SD.open(fader);
  Serial.println("Go");
  int i = 0;
  while(file.available())
  { 
    frame2_data[i] = file.read();
    i = i + 1;
  }
  return frame2_data[4200];
  file.close();
}

int readSerial() {
  
}
void setup() {
  //DIP-Setup 
  setupDipPins();
  //Serial Initilazing
  Serial.begin(9600);
  //DMX initializing 
  DMX::Initialize();
  //SD Card initializing
  SD.begin(5);
  //Normal LED initializing 
  //ledcSetup(1, 5000, 8);
  //ledcAttachPin(22, 1);
  //Fast LED Neopixel initializing 
  FastLED.addLeds<WS2812B, MATRIX_PIN, RGB>(leds, NUM_LEDS); // for GRB LEDs
  FastLED.setBrightness(255);
  //Check if SD Card is mounted:
  if(!SD.begin()){
    Serial.println("Card Mount Failed");
    return;
  } 
  //Clear all LEDs 
  FastLED.clear();
  FastLED.show();
  //Set the DIP Switches 
  dipChannelValue = calculateDMXChannelFromDIPSwitchSettings();
  //Serial.println(calculateDMXChannelFromDIPSwitchSettings());
}

static void setupDipPins()
{
  for(uint8_t i=0; i < 8; ++i)
    pinMode(dipPins[i], INPUT_PULLUP);
}

void loop() {      
      getRgbValues("/fader1");
      int val = 0;
      for (int i = 0; i < 1400; i++){
        leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
        // Variables add 
        val = val + 3;
      }
      FastLED.show();
      delay(5000);
      
      getRgbValues("/fader2");
      val = 0;
      for (int i = 0; i < 1400; i++){
        leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
        // Variables add 
        val = val + 3;
      }
      FastLED.show();
      delay(5000);
      
      getRgbValues("/fader3");
      val = 0;
      for (int i = 0; i < 1400; i++){
        leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
        // Variables add 
        val = val + 3;
      }
      FastLED.show();
      delay(5000);
 
      /*
      //Channel 1  is currently out of use... 
      /*readDmxChannel(0);
      if (channelstate != channelstate1_old){
        if (channelstate == true) {
          frame0getRgbValues("/animation/frame0");
          frame1getRgbValues("/animation/frame1");
          frame2getRgbValues("/animation/frame2");
          while(true){
            int val = 0;
            for (int i = 0; i < 1400; i++){
              leds[i] = CRGB(frame0_data[val], frame0_data[val + 1], frame0_data[val + 2]);
              // Variables add 
              val = val + 3;
            }
            FastLED.show();
            val = 0;
            for (int i = 0; i < 1400; i++){
              leds[i] = CRGB(frame1_data[val], frame1_data[val + 1], frame1_data[val + 2]);
              // Variables add 
              val = val + 3;
            }
            FastLED.show();
            val = 0;
            for (int i = 0; i < 1400; i++){
              leds[i] = CRGB(frame2_data[val], frame2_data[val + 1], frame2_data[val + 2]);
              // Variables add 
              val = val + 3;
            }
            FastLED.show();
          }
        }
        else {
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate1_old = channelstate; 
      //Channel 2
      readDmxChannel(1);
      if (channelstate != channelstate2_old){
        if (channelstate == true) {
          getRgbValues("/fader2");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate2_old = channelstate;
    
      //Channel 3
      readDmxChannel(2);
      if (channelstate != channelstate3_old){
        if (channelstate == true) {
          getRgbValues("/fader3");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate3_old = channelstate;
    
      //Channel 4
      readDmxChannel(3);
      if (channelstate != channelstate4_old){
        if (channelstate == true) {
          getRgbValues("/fader4");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate4_old = channelstate;
    
      //Channel 5
      readDmxChannel(4);
      if (channelstate != channelstate5_old){
        if (channelstate == true) {
          getRgbValues("/fader5");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate5_old = channelstate;
    
      //Channel 6
      readDmxChannel(5);
      if (channelstate != channelstate6_old){
        if (channelstate == true) {
          getRgbValues("/fader6");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate6_old = channelstate;
    
      //Channel 7
      readDmxChannel(6);
      if (channelstate != channelstate7_old){
        if (channelstate == true) {
          getRgbValues("/fader7");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate7_old = channelstate;
    
      //Channel 8
      readDmxChannel(7);
      if (channelstate != channelstate8_old){
        if (channelstate == true) {
          getRgbValues("/fader8");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
            //String printout0 = "leds[";
            //String printout1 = "] = CRGB(";
            //String printout2 = ",";
            //String printout3 = ",";
            //String printout4 = ");";
            //String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
            //Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate8_old = channelstate;
    
      //Channel 9
      readDmxChannel(8);
      if (channelstate != channelstate9_old){
        if (channelstate == true) {
          getRgbValues("/fader9");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
           // String printout0 = "leds[";
           // String printout1 = "] = CRGB(";
           // String printout2 = ",";
           // String printout3 = ",";
           // String printout4 = ");";
           // String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
           // Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate9_old = channelstate;
    
      //Channel 10
      readDmxChannel(9);
      if (channelstate != channelstate10_old){
        if (channelstate == true) {
          getRgbValues("/fader10");
          int val = 0;
          for (int i = 0; i < 1400; i++){
            // COnsole Print out 
           // String printout0 = "leds[";
           // String printout1 = "] = CRGB(";
           // String printout2 = ",";
           // String printout3 = ",";
           // String printout4 = ");";
           // String printoutges = printout0 + i + printout1 + file_data[val] + printout2 + file_data[val + 1] + printout3  + file_data[val + 2] + printout4;
           // Serial.println(printoutges);
            //LEDs execute: 
            leds[i] = CRGB(file_data[val], file_data[val + 1], file_data[val + 2]);
            // Variables add 
            val = val + 3;
          }
          FastLED.show();
        }
        else {
          Serial.println("The fader went oof !");
          //Clear all LEDs 
          FastLED.clear();
          FastLED.show();
        }
      }
      channelstate10_old = channelstate;
    }   */
}
int readDmxChannel(int x) {
  value = DMX::Read(dipChannelValue + x);
  if (value > 0) {
    channelstate = true;
    return channelstate;
  }  
  else if (value == 0){
    channelstate = false;
    return channelstate;
   }
}   

static uint8_t calculateDMXChannelFromDIPSwitchSettings(){
  uint8_t returnValue = 0;
  for(uint8_t i=0; i < 8; ++i)
    returnValue += (!digitalRead(dipPins[i]) << i);

  return returnValue;
}
  
