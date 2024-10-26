#include <SPI.h>
#include <LoRa.h>

//define the pins used by the transceiver module
#define NSS 10
#define RST 9
#define DIO0 2

String loraString = "";
int val = 0;

void setup() {
  //Initialize the serial monitor
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Receiver");

   //setup LoRa NSS, RST and DIO0 pins for transceiver module
  LoRa.setPins(NSS, RST, DIO0);

  // select the frequency according to your module. most commom frequences are 433E6,866E6 and 915E6
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  // Change sync word (0xF3) to match the receiver
  // This is a unique message id. The sync word use to assures taht LoRa messages don't match to other LoRa transceivers
  // 0-0xFF range
  LoRa.setSyncWord(0xF3);
  Serial.println("LoRa Initializing OK!");
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // received a packet
    Serial.print("Received packet '");

    // read packet
    while (LoRa.available()) {
      // read the message from lora transmitter
      Serial.print((char)LoRa.read());
    }
    Serial.println();

    // print RSSI of packet
    Serial.print("' with RSSI ");
    Serial.println(LoRa.packetRssi());
  }
}