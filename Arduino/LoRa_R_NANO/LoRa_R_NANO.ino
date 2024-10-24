#include <SPI.h>
#include <LoRa.h>

#define SS 10     // Pin per NSS (CS)
#define RST 9   // Pin per Reset
#define DIO0 2  // Pin per DIO0

void setup() {
  // Inizializzazione della comunicazione seriale
  Serial.begin(9600);
  while (!Serial);

  // Imposta i pin
  LoRa.setPins(SS, RST, DIO0);

  // Inizializza LoRa a 433 MHz
  if (!LoRa.begin(433E6)) {
    Serial.println("Errore di avvio LoRa!");
    while (1);
  }
  
  // Imposta i parametri per il ricevitore
  LoRa.setSignalBandwidth(500E3);  // Banda a 500 kHz
  LoRa.setSpreadingFactor(7);      // Spreading Factor a 7
  LoRa.setCodingRate4(5);          // Coding Rate a 4/5

  Serial.println("Ricevitore LoRa avviato.");
}

void loop() {
  // Controlla se c'è un pacchetto disponibile
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Legge il pacchetto
    Serial.print("Pacchetto ricevuto: ");

    while (LoRa.available()) {
      String received = LoRa.readString();
      Serial.print(received);
    }
    
    // Stampa il livello del segnale ricevuto (RSSI)
    Serial.print("  con RSSI ");
    Serial.println(LoRa.packetRssi());
  }
}
