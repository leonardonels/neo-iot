import spidev
import RPi.GPIO as GPIO
from time import sleep

# Pin configuration
RST_PIN = 22
DIO0_PIN = 27
CS_PIN = 25

# LoRa register addresses (consts)
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_PA_CONFIG = 0x09
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_MODEM_CONFIG1 = 0x1D
REG_MODEM_CONFIG2 = 0x1E
REG_MODEM_CONFIG3 = 0x26
REG_PAYLOAD_LENGTH = 0x22
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_ADDR_PTR = 0x0D
REG_IRQ_FLAGS = 0x12

# LoRa operational modes
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x83
MODE_LORA = 0x80

# LoRa configuration values
MAX_POWER = 0xF0                   # Maximum transmission power
BANDWIDTH_500KHZ = 0x72            # Bandwidth 500 kHz, Coding Rate 4/5
SPREADING_FACTOR_7 = 0x74          # Spreading Factor 7
CODING_RATE_4_5 = 0x04             # Additional configuration, Coding Rate 4/5

# Interrupt Flags
IRQ_TX_DONE_MASK = 0x08

# Most Significative Bit (MSB)
MSB_1 = 0x80
MSB_0 = 0x7F

REG_VERSION = 0x42  # Registro per leggere la versione

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DIO0_PIN, GPIO.IN)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.output(CS_PIN, GPIO.HIGH)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

# Funzione di verifica del modulo
def check_module():
    version = read_register(REG_VERSION)
    print(f"Module version: {version}")

# Function to write on LoRa register
def write_register(address, data):
    GPIO.output(CS_PIN, GPIO.LOW)
    spi.xfer([address | MSB_1, data])  # Set MSB to 1 for write operation
    GPIO.output(CS_PIN, GPIO.HIGH)

# Function to read from LoRa register
def read_register(address):
    GPIO.output(CS_PIN, GPIO.LOW)
    response = spi.xfer([address & MSB_0, 0x00])  # MSB 0 for read operation, 0x00 is just a dummy to set the clock for the read
    GPIO.output(CS_PIN, GPIO.HIGH)
    return response[1]

# Reset LoRa module
def reset_lora():
    GPIO.output(RST_PIN, GPIO.LOW)
    sleep(0.1)
    GPIO.output(RST_PIN, GPIO.HIGH)
    sleep(0.1)

# Initialize LoRa transmitter
def init_lora():
    reset_lora()
    write_register(REG_OP_MODE, MODE_LORA | MODE_STDBY)  # Set LoRa mode, standby mode
    sleep(0.1)

    mode = read_register(REG_OP_MODE)
    print(f"Current mode after standby setup: {mode}")

    write_register(REG_PA_CONFIG, MAX_POWER)  # Set max power
    write_register(REG_MODEM_CONFIG1, BANDWIDTH_500KHZ)  # Set bandwidth to 500 kHz, coding rate to 4/5
    write_register(REG_MODEM_CONFIG2, SPREADING_FACTOR_7)  # Set spreading factor to SF7
    write_register(REG_MODEM_CONFIG3, CODING_RATE_4_5)  # Additional configuration

    print(f"PA_CONFIG: {read_register(REG_PA_CONFIG)}")
    print(f"MODEM_CONFIG1: {read_register(REG_MODEM_CONFIG1)}")
    print(f"MODEM_CONFIG2: {read_register(REG_MODEM_CONFIG2)}")
    print(f"MODEM_CONFIG3: {read_register(REG_MODEM_CONFIG3)}")

    write_register(REG_FIFO_TX_BASE_ADDR, 0x80)  # Set FIFO Tx base address
    write_register(REG_FIFO_RX_BASE_ADDR, 0x80)  # Set FIFO Rx base address

    print(f"FIFO_TX_BASE_ADDR: {read_register(REG_FIFO_TX_BASE_ADDR)}")
    print(f"FIFO_RX_BASE_ADDR: {read_register(REG_FIFO_RX_BASE_ADDR)}")

    print("Module initialized.")

# Send a message
def send_message(message):
    write_register(REG_OP_MODE, MODE_LORA | MODE_TX)  # Set LoRa mode, Tx mode
    write_register(REG_FIFO_ADDR_PTR, 0x80)  # Set FIFO pointer to Tx base address
    print("Tx mode selected")

    # Write message to FIFO
    for byte in message.encode():
        write_register(REG_FIFO, byte)
    print("Message written to FIFO")

    # Set payload length
    write_register(REG_PAYLOAD_LENGTH, len(message))
    print("Payload length set")

    # Start transmission
    write_register(REG_OP_MODE, MODE_LORA | MODE_TX)
    print("Transmission started")
    
    # Verifica che il modulo sia effettivamente in MODE_TX
    mode = read_register(REG_OP_MODE)
    if mode != (MODE_LORA | MODE_TX):
        print(f"Warning: The module is not in TX mode. Current mode: {mode}")
    
    # Wait for TxDone flag
    while GPIO.input(DIO0_PIN) == 0:
        irq_flags = read_register(REG_IRQ_FLAGS)
        if irq_flags & IRQ_TX_DONE_MASK:
            break
        sleep(0.1)
    print("TxDone flag received")

    # Clear TxDone flag
    write_register(REG_IRQ_FLAGS, IRQ_TX_DONE_MASK)
    print("TxDone flag cleared")


try:
    check_module()
    print("starting...")
    init_lora()
    print("LoRa initiated!")
    while True:
        send_message("Hello World!")
        print("Message sent: Hello World!")
        sleep(5)
except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()
