# main.py
import LoRa as lora
import time
import paho.mqtt.client as mqtt

# Configura il modulo LoRa
lora.setup(cs_pin_number=25, rst_pin_number=22, dio0_pin_number=27, frequency=433E6, debug=True)

# Inizializza LoRa
lora.begin()

# Configura MQTT per TTN
TTN_BROKER = "eu1.cloud.thethings.network"
TTN_PORT = 1883
TTN_APP_ID = "your-app-id"  # Sostituisci con il tuo Application ID
TTN_ACCESS_KEY = "your-access-key"  # Sostituisci con la tua access key
TTN_TOPIC = "v3/{}/devices/{}/up".format(TTN_APP_ID, "your-device-id")  # Sostituisci con l'ID del dispositivo

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(TTN_APP_ID, password=TTN_ACCESS_KEY)
mqtt_client.connect(TTN_BROKER, TTN_PORT, 60)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to TTN with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message Published")

mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

def send_to_ttn(payload):
    mqtt_client.publish(TTN_TOPIC, payload)

def receive_and_send():
    while True:
        lora.receive(timeout=10)  # Ricevi messaggi LoRa
        message = "Sample message"  # Sostituisci con il messaggio ricevuto
 
