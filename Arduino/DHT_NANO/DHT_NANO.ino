#include "DHT.h"

#define DHTPIN 2     // Pin al quale è collegato il sensore DHT11
#define DHTTYPE DHT11   // Definisci il tipo di sensore (DHT11)

DHT dht(DHTPIN, DHTTYPE);  // Inizializza il sensore DHT

void setup() {
  Serial.begin(9600);
  Serial.println("DHT11 Test");

  dht.begin();  // Avvia il sensore DHT
}

void loop() {
  // Attendi un po' prima di ogni lettura
  delay(2000);

  // Legge la temperatura e l'umidità
  float h = dht.readHumidity();
  float t = dht.readTemperature();  // Temperatura in gradi Celsius

  // Controlla se le letture sono valide
  if (isnan(h) || isnan(t)) {
    Serial.println("Errore nella lettura del sensore DHT11!");
    return;
  }

  // Stampa i valori letti
  Serial.print("Umidità: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperatura: ");
  Serial.print(t);
  Serial.println(" °C");
}
