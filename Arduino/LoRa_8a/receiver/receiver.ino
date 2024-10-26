#include <SPI.h>
#include <LoRa.h>

//define the pins used by the receiver module
#define NSS 10
#define RST 9
#define DIO0 2

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Receiver");

  //setup LoRa NSS, RST and DIO0 pins for receiver module
  LoRa.setPins(NSS, RST, DIO0);
  //LoRa.setFrequency(5E6); //5 MHz

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  LoRa.setSignalBandwidth(500E3);
  LoRa.setSpreadingFactor(7);
  LoRa.setCodingRate4(5);

  //LoRa.dumpRegisters(Serial);
  Serial.println("LoRa Receiver initated!");
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // received a packet
    Serial.print("Received packet '");

    // read packet
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }

    // print RSSI of packet
    Serial.print("' with RSSI ");
    Serial.println(LoRa.packetRssi());
  }
}