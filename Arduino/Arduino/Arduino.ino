#include <SPI.h>
#include <LoRa.h>
#include <Cipher.h>
#include <AES.h>
#include <CBC.h>
#include <string.h>
#include <EEPROM.h>

#ifdef ARDUINO_SAMD_MKRWAN1300
#error "This example is not compatible with the Arduino MKR WAN 1300 board!"
#endif

//define the pins used by the receiver module
#define NSS 10
#define RST 9
#define DIO0 2
#define FREQ 433E6
#define BW 500E3
#define SF 7
#define CR 5

long uniqueId; 

uint8_t key[16] = {0xC3, 0x24, 0x64, 0x98, 0xDE, 0x56, 0x5D, 0x8C, 
                  0x55, 0x88, 0x7C, 0x05, 0x86, 0xF9, 0x82, 0x26};

//-----------------------------------------------------------------

void unpadPKCS7(uint8_t *data, size_t &length) {
  uint8_t padding_value = data[length - 1];
  length -= padding_value;
}

void padPKCS7(uint8_t* data, size_t &length, size_t block_size) {
  size_t padding_length = block_size - (length % block_size);
  for (size_t i = 0; i < padding_length; i++) {
    data[length + i] = (uint8_t)padding_length;
  }
  length += padding_length;
}

char* decrypt_message(int packetSize) {
  uint8_t received_message[packetSize];
  int i = 0;

  // read all received bytes and saves them
  while (LoRa.available()) {
    received_message[i++] = LoRa.read();
  }

  // extract iv from the first 16 bytes
  uint8_t iv[16];
  memcpy(iv, received_message, 16);

  // extract the cyphertext
  size_t ciphertext_length = packetSize - 16;
  uint8_t ciphertext[ciphertext_length];
  memcpy(ciphertext, received_message + 16, ciphertext_length);

  uint8_t plaintext[ciphertext_length];

  // configure AES and CBC to decipher the message
  CBC<AES128> cbc;
  cbc.setKey(key, sizeof(key));
  cbc.setIV(iv, sizeof(iv));

  cbc.decrypt(plaintext, ciphertext, ciphertext_length);

  // remove the padding PKCS7
  size_t plaintext_length = ciphertext_length;
  unpadPKCS7(plaintext, plaintext_length);

  char* decrypted_message = (char*)malloc(plaintext_length + 1);
  if (decrypted_message == NULL) {
    printf("Error during memory allocation\n");
    return NULL;
  }
  size_t j=0;
  for (; j < plaintext_length; j++) {
    decrypted_message[j] = (char)plaintext[j];
  }
  decrypted_message[j] = '\0';
  return decrypted_message;
}

void onReceive_encrypted(int packetSize) {
  Serial.print("Received ecrypted packet '");
  char* decrypted_message=decrypt_message(packetSize);
  Serial.print(decrypted_message);
  
  // print RSSI of packet
  Serial.print("' with RSSI ");
  Serial.println(LoRa.packetRssi());
  // to use in conjunction with a state machine
}

void onReceive(int packetSize) {
  // received a packet
  Serial.print("Received packet '");

  //LoRa.dumpRegisters(Serial);

  // read packet
  for (int i = 0; i < packetSize; i++) {
    Serial.print((char)LoRa.read());
  }

  // print RSSI of packet
  Serial.print("' with RSSI ");
  Serial.println(LoRa.packetRssi());
}

void lora_encrypted_receiver(){
  Serial.println("LoRa Receiver Callback");

  // register the receive callback
  LoRa.onReceive(onReceive_encrypted);

  // put the radio into receive mode
  LoRa.receive();
}

void lora_receiver(){
  Serial.println("LoRa Receiver Callback");

  // register the receive callback
  LoRa.onReceive(onReceive);

  // put the radio into receive mode
  LoRa.receive();
}

void lora_transmitter(const String &message){
  Serial.print("Sending packet: ");
  Serial.println(message);
  
  // send packet 
  LoRa.beginPacket();
  LoRa.write((byte*)&uniqueId, sizeof(uniqueId));
  LoRa.print(message);
  LoRa.endPacket();
}

void lora_encrypted_transmitter(const String &message){
  Serial.print("Sending encrypted packet: ");
  Serial.println(message);

  uint8_t iv[16];
  for (int i = 0; i < 16; i++) {
    iv[i] = random(0, 256);  // Genera IV casuale
  }

  uint8_t message_bytes[message.length()];
  message.getBytes(message_bytes, message.length() + 1);

  size_t message_length = message.length();
  padPKCS7(message_bytes, message_length, 16);

  uint8_t ciphertext[message_length];
  CBC<AES128> cbc;
  cbc.setKey(key, sizeof(key));
  cbc.setIV(iv, sizeof(iv));

  cbc.encrypt(ciphertext, message_bytes, message_length);

  LoRa.beginPacket();
  LoRa.write(iv, sizeof(iv));
  LoRa.write((byte*)&uniqueId, sizeof(uniqueId));
  LoRa.write(ciphertext, message_length);
  LoRa.endPacket();
  Serial.println("Encrypted packet sent!");
}

void lora_begin(){
  LoRa.setPins(NSS, RST, DIO0);

  if (!LoRa.begin(FREQ)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  LoRa.setSignalBandwidth(BW);
  LoRa.setSpreadingFactor(SF);
  LoRa.setCodingRate4(CR);

  //LoRa.dumpRegisters(Serial);
  Serial.println("LoRa initated!");
}

long getOrGenerateUniqueId() {
  // Inizialise the EEPROM
  EEPROM.begin(512);

  // Use the first byte of the memory EEPROM for determine if the ID was already written
  if (EEPROM.read(0) == 0xFF) {
    long uniqueId = millis() + random(1000, 9999);
    EEPROM.write(0, (uniqueId >> 8) & 0xFF);
    EEPROM.write(1, uniqueId & 0xFF);
    EEPROM.commit();
    Serial.print("Generated unique ID: ");
    Serial.println(uniqueId);
    return uniqueId;
  } else {
    long existingId = EEPROM.read(0) << 8 | EEPROM.read(1);
    Serial.print("Existing unique ID: ");
    Serial.println(existingId);
    return existingId;
  }
}



void setup() {
  Serial.begin(9600);
  while (!Serial);

  uniqueId = getOrGenerateUniqueId();
  Serial.print("Unique ID: ");
  Serial.println(uniqueId);

  lora_begin();
  //lora_encrypted_receiver();
}

void loop() {
  // do nothing
  // or
  lora_encrypted_transmitter("Hello World!");
  delay(2000);
}

/*
'0x0: 0x39
0x1: 0x85
0x2: 0x1A
0x3: 0xB
0x4: 0x0
0x5: 0x52
0x6: 0x6C
0x7: 0x40
0x8: 0x0
0x9: 0x8F
0xA: 0x9
0xB: 0x2B
0xC: 0x23
0xD: 0x1
0xE: 0x0
0xF: 0x0
0x10: 0x0
0x11: 0x0
0x12: 0x0
0x13: 0x10
0x14: 0x0
0x15: 0x1
0x16: 0x0
0x17: 0x0
0x18: 0x24
0x19: 0x17
0x1A: 0x79
0x1B: 0x40
0x1C: 0x0
0x1D: 0x92
0x1E: 0x70
0x1F: 0x64
0x20: 0x0
0x21: 0x8
0x22: 0x1
0x23: 0xFF
0x24: 0x0
0x25: 0x10
0x26: 0x4
0x27: 0x0
0x28: 0x0
0x29: 0x4
0x2A: 0xC0
0x2B: 0x0
0x2C: 0xE
0x2D: 0x50
0x2E: 0x14
0x2F: 0x40
0x30: 0x0
0x31: 0xC3
0x32: 0x5
0x33: 0x27
0x34: 0x1C
0x35: 0xA
0x36: 0x3
0x37: 0xA
0x38: 0x42
0x39: 0x12
0x3A: 0x58
0x3B: 0x1D
0x3C: 0x0
0x3D: 0xAF
0x3E: 0x0
0x3F: 0x0
0x40: 0x0
0x41: 0x0
0x42: 0x12
0x43: 0x24
0x44: 0x2D
0x45: 0x0
0x46: 0x3
0x47: 0x0
0x48: 0x4
0x49: 0x23
0x4A: 0x0
0x4B: 0x9
0x4C: 0x5
0x4D: 0x84
0x4E: 0x32
0x4F: 0x2B
0x50: 0x14
0x51: 0x0
0x52: 0x0
0x53: 0xD
0x54: 0x0
0x55: 0x0
0x56: 0x0
0x57: 0xF
0x58: 0xE0
0x59: 0x0
0x5A: 0xC
0x5B: 0xF6
0x5C: 0x7
0x5D: 0x0
0x5E: 0x5C
0x5F: 0x78
0x60: 0x0
0x61: 0x1C
0x62: 0xE
0x63: 0x5B
0x64: 0xCC
0x65: 0x0
0x66: 0x1
0x67: 0x50
0x68: 0x0
0x69: 0x0
0x6A: 0x0
0x6B: 0x0
0x6C: 0x0
0x6D: 0x0
0x6E: 0x0
0x6F: 0xB
0x70: 0xD0
0x71: 0x0
0x72: 0x14
0x73: 0x0
0x74: 0x0
0x75: 0x0
0x76: 0x0
0x77: 0x0
0x78: 0x0
0x79: 0x0
0x7A: 0x0
0x7B: 0x0
0x7C: 0x0
0x7D: 0x0
0x7E: 0x0
0x7F: 0x0
*/
