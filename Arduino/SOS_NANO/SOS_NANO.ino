// Definizione dei tempi per il codice Morse
#define DOT_DURATION 250   // Durata del punto (millisecondi)
#define DASH_DURATION 750  // Durata della linea (millisecondi)
#define GAP_DURATION 250   // Spazio tra punti e linee (millisecondi)
#define LETTER_GAP 750     // Spazio tra lettere (millisecondi)
#define WORD_GAP 1500      // Spazio tra parole (millisecondi)

// Definizione del pin del LED
int ledPin = LED_BUILTIN; // Usa il pin GPIO 2 su ESP32

void setup() {
  // Imposta il pin del LED come output
  pinMode(ledPin, OUTPUT);
}

void loop() {
  // SOS in codice Morse: ... --- ...
  // S: tre punti (dot)
  dot();
  dot();
  dot();

  delay(LETTER_GAP); // Spazio tra lettere

  // O: tre linee (dash)
  dash();
  dash();
  dash();

  delay(LETTER_GAP); // Spazio tra lettere

  // S: tre punti (dot)
  dot();
  dot();
  dot();

  delay(WORD_GAP); // Spazio tra parole (prima di ripetere SOS)
}

// Funzione per accendere il LED come un punto (dot)
void dot() {
  digitalWrite(ledPin, HIGH);
  delay(DOT_DURATION);
  digitalWrite(ledPin, LOW);
  delay(GAP_DURATION);
}

// Funzione per accendere il LED come una linea (dash)
void dash() {
  digitalWrite(ledPin, HIGH);
  delay(DASH_DURATION);
  digitalWrite(ledPin, LOW);
  delay(GAP_DURATION);
}
