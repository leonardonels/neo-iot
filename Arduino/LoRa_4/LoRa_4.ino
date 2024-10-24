#include <LoRa.h>

void setup() {
  Serial.begin(9600);

  LoRa.setPins(10, 2, 9); // NSS, DIO0, Reset
  
  // Inizializza LoRa alla frequenza desiderata (es. 433E6 per 433 MHz)
  if (!LoRa.begin(433E6)) {
    Serial.println("Errore di inizializzazione LoRa!");
    while (1);
  }

  // Imposta la banda a 500 kHz
  LoRa.setSignalBandwidth(500E3);
  
  // Imposta lo Spreading Factor a 7
  LoRa.setSpreadingFactor(7);
  
  // Imposta il Coding Rate a 4/5
  LoRa.setCodingRate4(5);

  Serial.println("LoRa inizializzato con successo!");
}

void loop() {
  Serial.println("Hello, world!");

  // Esempio di invio messaggio
  LoRa.beginPacket();
  LoRa.print("Hello, world!");
  LoRa.endPacket();
  
  delay(5000);  // Ritardo tra i pacchetti
}
