#deprecated

import LoRa as lora
import socket
import json
from time import sleep, time

# Configura i parametri per la connessione al server TTN
WIRELESS = True
TTN_GATEWAY_ADDRESS = "router.eu.thethings.network"  # Sostituisci con il server TTN appropriato
TTN_GATEWAY_PORT = 1700
GATEWAY_EUI = "B827EBFFFEF7XXXX"  # Inserisci l'ID del tuo gateway
GATEWAY_EUI_WIRELESS = "B827EBFFFEF7XXXX"  # Inserisci l'ID del tuo gateway
UDP_PORT = 1700

# Configurazione LoRa per ricezione continua
FREQUENCY = 433  # Frequenza per l'Europa per TTN
BANDWIDTH = 0x90  # 125 kHz
SPREADING_FACTOR = 0x74  # Spreading Factor 7 (0x74)
CODING_RATE = 0x04  # Coding rate 4/5 (0x04)
TIMEOUT = 10  # Timeout di ricezione in secondi

# Imposta l'interfaccia UDP per inviare dati al server TTN
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT))

def send_to_ttn(data):
    """
    Invia i dati ricevuti a TTN tramite UDP.
    """
    try:
        sock.sendto(data, (TTN_GATEWAY_ADDRESS, TTN_GATEWAY_PORT))
        print(f"Dati inviati a TTN: {data}")
    except Exception as e:
        print(f"Errore nell'invio a TTN: {e}")

def create_ttn_packet(payload):
    """
    Crea un pacchetto JSON per inviare i dati a TTN.
    """
    packet = {
        "rxpk": [
            {
                "time": "immediate",
                "tmst": int(time() * 1000000),  # Timestamp in microsecondi
                "freq": FREQUENCY,
                "chan": 0,
                "rfch": 0,
                "stat": 1,
                "modu": "LORA",
                "datr": "SF7BW125",
                "codr": "4/5",
                "lsnr": 10,
                "rssi": -40,  # Valore di esempio per RSSI
                "size": len(payload),
                "data": payload.encode('utf-8').hex()  # Converti il payload in formato hex
            }
        ]
    }
    return json.dumps(packet).encode('utf-8')

def main():
    # Configura il modulo LoRa
    lora.setup(cs_pin_number=25, rst_pin_number=22, dio0_pin_number=27, frequency=8000000, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=CODING_RATE)

    print("Gateway LoRa per TTN in esecuzione...")

    try:
        while True:
            # Ricezione di un messaggio LoRa
            message = lora.receive(TIMEOUT)
            if message:
                print(f"Messaggio LoRa ricevuto: {message}")
                
                # Crea pacchetto e invia a TTN
                ttn_packet = create_ttn_packet(message)
                send_to_ttn(ttn_packet)
            sleep(0.1)

    except KeyboardInterrupt:
        print("Chiusura del gateway LoRa.")
    finally:
        lora.close()
        sock.close()

if __name__ == "__main__":
    main()
