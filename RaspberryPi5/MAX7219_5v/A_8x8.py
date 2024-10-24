import spidev
import RPi.GPIO as GPIO
from time import sleep

_rows = 8

# Configura il GPIO per gestire il Chip Select
CS_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.output(CS_PIN, GPIO.HIGH)

# Inizializza l'interfaccia SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, device 0 (CS0)
spi.max_speed_hz = 1000000  # 1 MHz

# Funzione per scrivere sul registro del MAX7219
def write_register(address, data):
    GPIO.output(CS_PIN, GPIO.LOW)  # Abbassa CS
    spi.xfer([address, data])      # Invia l'indirizzo e i dati
    GPIO.output(CS_PIN, GPIO.HIGH) # Alza CS

# Inizializza il MAX7219
def initialize_max7219():
    write_register(0x09, 0x00)  # No decodifica BCD
    write_register(0x0A, 0x03)  # Intensità media
    write_register(0x0B, 0x07)  # Abilita tutte e 8 le cifre
    write_register(0x0C, 0x01)  # Accendi il display
    write_register(0x0F, 0x00)  # Disabilita la modalità test

# Visualizza un pattern sulla matrice LED
def display_pattern(pattern):
    for i in range(_rows):
        write_register(i + 1, pattern[i])

# Pattern esempio per il LED matrix 8x8 (carattere "A")
pattern_A = [
    0b00000000,  # Riga 1
    0b00011000,  # Riga 2
    0b00100100,  # Riga 3
    0b01000010,  # Riga 4
    0b01111110,  # Riga 5
    0b01000010,  # Riga 6
    0b01000010,  # Riga 7
    0b00000000   # Riga 8
]

# Avvia il programma
initialize_max7219()
display_pattern(pattern_A)

#try:
#    while True:
#        sleep(1)  # Mantiene il pattern sul display
#except KeyboardInterrupt:
#    spi.close()  # Chiudi l'interfaccia SPI
#    GPIO.cleanup()  # Ripristina i GPIO

spi.close()
GPIO.cleanup()