#include <LoRa.h>

void setup() {
  Serial.begin(9600);

  LoRa.begin(433E6);  // Imposta la frequenza a 433 MHz

  // Imposta la banda a 500kHz, SF7, Coding Rate 4/5
  LoRa.setSignalBandwidth(500E3);    // Banda di 500 kHz
  LoRa.setSpreadingFactor(7);        // Spreading Factor 7
  LoRa.setCodingRate4(5);            // Codifica 4/5
}

void loop() {
  // Trasmetti un numero ogni 2 secondi
  LoRa.beginPacket();
  LoRa.print("1234");
  LoRa.endPacket();
  delay(2000);
}
