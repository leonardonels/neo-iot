import spidev
import time
from gpiozero import DigitalOutputDevice, Button
import RPi.GPIO as GPIO

# Imposta i pin per CS, RESET e DIO0
CS_PIN = 8   # NSS
RESET_PIN = 25
DIO0_PIN = 24

# Inizializzazione GPIO
reset_pin = DigitalOutputDevice(RESET_PIN)
dio0_pin = Button(DIO0_PIN)

# Inizializzazione SPI
spi = spidev.SpiDev(0, 0)  # Utilizza SPI0, CE0 (GPIO 8 per CS)
spi.max_speed_hz = 5000000

# Funzioni per interagire con il modulo LoRa
def spi_write(register, value):
    spi.xfer2([register | 0x80, value])

def spi_read(register):
    return spi.xfer2([register & 0x7F, 0])[1]

# Inizializzazione del modulo LoRa
def lora_init():
    # Reset del modulo LoRa
    reset_pin.off()
    time.sleep(0.01)
    reset_pin.on()
    time.sleep(0.01)

    # Imposta la modalità sleep (per la configurazione)
    spi_write(0x01, 0x80)  # Modalità sleep

    # Imposta la frequenza a 433 MHz
    spi_write(0x06, 0x6C)
    spi_write(0x07, 0x80)
    spi_write(0x08, 0x00)

    # Imposta la larghezza di banda a 500 kHz, SF7, CR4/5
    spi_write(0x1D, 0x92)  # Larghezza di banda
    spi_write(0x1E, 0x74)  # SF7, CR4/5

    # Modalità ricezione continua
    spi_write(0x01, 0x85)

    print("Modulo LoRa inizializzato e in modalità ricezione")

# Funzione per leggere pacchetti ricevuti
def lora_receive():
    if dio0_pin.is_pressed:
        irq_flags = spi_read(0x12)  # Leggi i flag di interrupt
        if irq_flags & 0x40:  # Controlla se c'è un pacchetto ricevuto
            # Leggi il pacchetto
            spi_write(0x12, 0xFF)  # Resetta i flag di interrupt
            packet_len = spi_read(0x13)
            spi_write(0x0D, 0x00)  # Punta all'indirizzo del buffer
            payload = [spi_read(0x00) for _ in range(packet_len)]
            rssi_value = spi_read(0x1A) - 157  # RSSI

            print(f"Pacchetto ricevuto: {''.join(chr(b) for b in payload)}")
            print(f"RSSI: {rssi_value}")
        else:
            print("Nessun pacchetto ricevuto")

# Inizializza il modulo LoRa
lora_init()

# Ciclo principale per ricevere pacchetti
try:
    while True:
        lora_receive()
        time.sleep(1)
except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()
