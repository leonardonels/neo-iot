import spidev
import RPi.GPIO as GPIO
import time

# Configurazione dei pin GPIO
SS_PIN = 8  # Pin per Select Slave (CE0 o CE1 in base alla configurazione hardware)
DIO0_PIN = 22  # Pin per interrupt su DIO0

# Inizializzazione della comunicazione SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, dispositivo 0
spi.max_speed_hz = 500000

# Funzione per scrivere sui registri LoRa
def write_register(register, value):
    spi.xfer2([register | 0x80, value])

# Funzione per leggere dai registri LoRa
def read_register(register):
    return spi.xfer2([register & 0x7F, 0x00])[1]

# Configurazione del GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SS_PIN, GPIO.OUT)
GPIO.setup(DIO0_PIN, GPIO.IN)

# Funzione per inizializzare il modulo LoRa
def lora_init():
    GPIO.output(SS_PIN, GPIO.HIGH)
    time.sleep(0.1)
    
    # Metti LoRa in modalità sleep per configurazione
    write_register(0x01, 0x80)  # Modalità sleep
    
    # Imposta frequenza a 433 MHz
    write_register(0x06, 0x6C)
    write_register(0x07, 0x80)
    write_register(0x08, 0x00)
    
    # Imposta banda, Spreading Factor e Coding Rate
    write_register(0x1D, 0x72)  # Imposta la banda a 500kHz, Coding Rate 4/5
    write_register(0x1E, 0x74)  # Spreading Factor 7
    
    # Imposta il modo di ricezione continua
    write_register(0x01, 0x85)  # Modalità LoRa RX continua

# Funzione per leggere un pacchetto LoRa
def lora_receive():
    # Attendi finché DIO0 non segnala che un pacchetto è stato ricevuto
    while GPIO.input(DIO0_PIN) == 0:
        time.sleep(0.1)
    
    # Leggi il numero di byte ricevuti
    irq_flags = read_register(0x12)
    if irq_flags & 0x40:  # RX Done
        # Leggi lunghezza del pacchetto ricevuto
        current_addr = read_register(0x10)
        received_count = read_register(0x13)
        
        # Leggi il pacchetto
        write_register(0x0D, current_addr)  # Punta al primo byte
        payload = []
        for i in range(received_count):
            payload.append(read_register(0x00))  # Leggi ogni byte
        
        # Resetta i flag di interrupt
        write_register(0x12, 0xFF)
        
        return bytes(payload)
    return None

# Main loop
try:
    lora_init()
    print("In ascolto per i messaggi LoRa...")
    while True:
        packet = lora_receive()
        if packet:
            print(f"Messaggio ricevuto: {packet}")
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    spi.close()
    GPIO.cleanup()
