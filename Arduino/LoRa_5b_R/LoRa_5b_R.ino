#include <SPI.h>
#include <LoRa.h>

// Configurazione pin (modifica se necessario)
const int csPin = 10;    // NSS
const int resetPin = 9;  // RESET
const int dioPin = 2;    // DIO0

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Configurazione pin
  LoRa.setPins(csPin, resetPin, dioPin);

  // Inizializzazione modulo LoRa
  if (!LoRa.begin(433E6)) { // Frequenza 433 MHz, assicurati che sia la stessa del trasmettitore
    Serial.println("LoRa init failed. Check your connections.");
    while (true);
  }
  
  LoRa.setSpreadingFactor(7);        // Spreading Factor SF7
  LoRa.setSignalBandwidth(500E3);    // Banda 500 kHz
  LoRa.setCodingRate4(5);            // Coding Rate 4/5

  Serial.println("LoRa Receiver initialized.");
}

void loop() {
  // Controllo per nuovo pacchetto ricevuto
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Messaggio ricevuto
    Serial.print("Received packet: ");
    while (LoRa.available()) {
      char incoming = (char)LoRa.read();
      Serial.print(incoming); // Stampa messaggio ricevuto
    }
    Serial.println();
  }
}
