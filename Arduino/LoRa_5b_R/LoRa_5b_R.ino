#include <SPI.h>
#include <LoRa.h>

//define the pins used by the transceiver module
#define NSS 10
#define RST 9
#define DIO0 2

int counter = 0;

void setup() {
  //Initialize the serial monitor
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Sender");

  //setup LoRa NSS, RST and DIO0 pins for transceiver module
  LoRa.setPins(NSS, RST, DIO0);
  //LoRa.setSPIFrequency(5E6); //5 MHz

  // select the frequency according to your module. most commom frequences are 433E6,866E6 and 915E6
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  LoRa.setSignalBandwidth(500E3);
  LoRa.setSpreadingFactor(7);
  LoRa.setCodingRate4(5);
}

void loop() {
  Serial.print("Sending packet: ");
  Serial.println(counter);
  
  // send packet 
  LoRa.beginPacket();
  LoRa.print(counter);
  LoRa.print(": Hello World!");
  LoRa.endPacket();

  counter++;
  delay(2000);
}
