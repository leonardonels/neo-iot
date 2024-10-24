#include <SPI.h>
#include <LoRa.h>

void setup() {
    Serial.begin(9600);
    LoRa.begin(433E6);
}

void loop() {
    // Invia un numero (esempio: 123)
    LoRa.beginPacket();
    LoRa.print(123);  // Invia il numero come stringa
    LoRa.endPacket();

    Serial.println("Sent: 123");
    delay(2000);  // Invia ogni 2 secondi
}
