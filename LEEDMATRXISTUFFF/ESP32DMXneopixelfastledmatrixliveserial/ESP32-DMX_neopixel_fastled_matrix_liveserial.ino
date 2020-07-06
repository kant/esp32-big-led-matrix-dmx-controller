#include <dmx.h>
#include <FastLED.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"


#define MATRIX_PIN 25
#define NUM_LEDS 49

int r;
int g;
int g1;
int b;
int b1;
int file_data[147];
int value;
bool channelstate;
bool channelstate_old = false;
int channel;
int const btn = 2;
String modus;
String incomingByte;
int read_byte;
int read_ascii;
int count_values = NUM_LEDS * 3;
String rwert;
String gwert;
String bwert;

CRGB leds[NUM_LEDS];

void setup() {
  //Serial Initilazing
  Serial.begin(9600);
  //SD Card initializing
  SD.begin(5);
  //Fast LED Neopixel initializing 
  FastLED.addLeds<WS2812B, MATRIX_PIN, RGB>(leds, NUM_LEDS); // for GRB LEDs
  FastLED.setBrightness(255);
  //Check if SD Card is mounted:
  if(!SD.begin()){
    Serial.print("Card Mount Failed");
    return;
  } 
  //Initialize LED
  pinMode(17, OUTPUT);
  //Clear all LEDs 
  FastLED.clear();
  FastLED.show();
  // Check Serial Connection:
}

void loop() {
  read_byte = Serial.read(); //--> Der Gesamte String ist "gespreichert". Bei jeden mal Serial.read wird der nächste byte(die nächste Zahl) ausgelesen.  
  if (read_byte > 0) { // Wenn ein String eingegeben wurde startet das Progrmam.: 
    map_byte_to_ascii(read_byte);
    Serial.println("Again");
    if (read_ascii == 1){  // Wenn es sich um einen Gültigen Werte-String handelt, führe den LED set Process aus.
      for(int i = 0; i < 49; i++){
        //First RBG Value
        Serial.read();  // Skip the Slash
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
        Serial.println(read_ascii);
        rwert = "";
        rwert += read_ascii;
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
          
        if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
          Serial.println(read_ascii);
          rwert += read_ascii;
          read_byte = Serial.read();  //Read first byte
          map_byte_to_ascii(read_byte);
            
          if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
            rwert += read_ascii;
          }
        }
        
        //second RGB Value
        Serial.read();  // Skip the Slash
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
        Serial.println(read_ascii);
        gwert = "";
        gwert += read_ascii;
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
          
        if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
          Serial.println(read_ascii);
          gwert += read_ascii;
          read_byte = Serial.read();  //Read first byte
          map_byte_to_ascii(read_byte);
            
          if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
            gwert += read_ascii;
          }
        }
  
        //Third RGB Value
        Serial.read();  // Skip the Slash
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
        Serial.println(read_ascii);
        bwert = "";
        bwert += read_ascii;
        read_byte = Serial.read();  //Read first byte
        map_byte_to_ascii(read_byte);
          
        if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
          Serial.println(read_ascii);
          bwert += read_ascii;
          read_byte = Serial.read();  //Read first byte
          map_byte_to_ascii(read_byte);
            
          if (read_ascii != 10){  // Wenn der Wert kein Slash ist: 
            bwert += read_ascii;
          }
        leds[i] = CRGB(rwert.toInt(), gwert.toInt(), bwert.toInt());
        FastLED.show();
      }
    
    //leds[1] = CRGB(0, incomingByte, 0);
    //leds[2] = CRGB(0, incomingByte, incomingByte);
    //leds[3] = CRGB(incomingByte, 0, incomingByte);
    //FastLED.show();
    //read_byte = Serial.read(); //Read again to delete the second.
    }
  }
}

float map_byte_to_ascii(int read_byte){
  if (read_byte == 48){
    read_ascii = 0;
  }
  else if (read_byte == 49){
    read_ascii = 1;
  }
  else if (read_byte == 50){
    read_ascii = 2;
  }
  else if (read_byte == 51){
    read_ascii = 3;
  }
  else if (read_byte == 52){
    read_ascii = 4;
  }
  else if (read_byte == 53){
    read_ascii = 5;
  }
  else if (read_byte == 54){
    read_ascii = 6;
  }
  else if (read_byte == 55){
    read_ascii = 7;
  }
  else if (read_byte == 56){
    read_ascii = 8;
  }
  else if (read_byte == 57){
    read_ascii = 9;
  }
  else if (read_byte == 47){
    read_ascii = 10;
  }
  
  return read_ascii;
}
