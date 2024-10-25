import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep

# Pin configuration
RST_PIN = 22
DIO0_PIN = 27
CS_PIN = 25

# LoRa register addresses (consts)
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_PA_CONFIG = 0x09
REG_MODEM_CONFIG1 = 0x1D
REG_MODEM_CONFIG2 = 0x1E
REG_MODEM_CONFIG3 = 0x26
REG_FIFO_ADDR_PTR = 0x0D
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_CURRENT_ADDR = 0x10
REG_PAYLOAD_LENGTH = 0x22
REG_IRQ_FLAGS = 0x12

REG_VERSION = 0x42  # Registro della versione del chip

# LoRa configuration values
MAX_POWER = 0xFF
BANDWIDTH_500KHZ = 0x72
SPREADING_FACTOR_7 = 0x74
CODING_RATE_4_5 = 0x04

# LoRa operational modes
MODE_LORA_SLEEP = 0x80
MODE_LORA_STDBY = 0x81
MODE_LORA_TX = 0x83
MODE_LORA = 0x80

# MSB settings
MSB_1 = 0x80
MSB_0 = 0x7F

# GPIO setup using gpiozero
reset_pin = OutputDevice(RST_PIN)
dio0_pin = InputDevice(DIO0_PIN)
cs_pin = OutputDevice(CS_PIN)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000  # 1 MHz

#...

def init_lora():
    reset_lora()
    write_register(REG_OP_MODE, MODE_LORA)
    write_register(REG_OP_MODE, MODE_LORA_STDBY)
    write_register(REG_PA_CONFIG, MAX_POWER)
    write_register(REG_MODEM_CONFIG1, BANDWIDTH_500KHZ)
    write_register(REG_MODEM_CONFIG2, SPREADING_FACTOR_7)
    write_register(REG_MODEM_CONFIG3, CODING_RATE_4_5)
    write_register(REG_FIFO_TX_BASE_ADDR, 0x80)
    write_register(REG_FIFO_RX_BASE_ADDR, 0x80)
    print("Module initialized.")
    check_mode()

    # Reset LoRa module
def reset_lora():
    reset_pin.off()
    sleep(0.1)
    reset_pin.on()
    sleep(0.1)

# Function to write on LoRa register
def write_register(address, data):
    cs_pin.off()
    spi.writebytes([address | MSB_1, data])
    cs_pin.on()
    sleep(0.01)

# Function to read from LoRa register
def read_register(address):
    cs_pin.off()
    spi.writebytes([address & MSB_0])
    response = spi.readbytes(1)
    cs_pin.on()
    return response[0]

def check_mode():
    current_mode = read_register(REG_OP_MODE)
    print(f"Current mode: {current_mode}")

# Send a message
def send_message(message):
    write_register(REG_FIFO_ADDR_PTR, 0x80)  # Set FIFO pointer to Tx base address
    print("FIFO pointer set")

    # Write message to FIFO
    for byte in message.encode():
        write_register(REG_FIFO, byte)
    print("Message written to FIFO")

    # Set payload length
    write_register(REG_PAYLOAD_LENGTH, len(message))
    print("Payload length set")

    # Start transmission
    write_register(REG_OP_MODE, MODE_LORA_TX)
    sleep(0.1)  # Ritardo per permettere al modulo di passare alla modalità di trasmissione
    check_mode()  # Controlla di nuovo la modalità
    print("Transmission started")

    # Check mode after setting to TX
    mode = read_register(REG_OP_MODE)
    if mode != (MODE_LORA_TX):
        print(f"Warning: The module is not in TX mode. Current mode: {mode}")

    # Wait for TxDone flag*
    while not dio0_pin.is_active:
        sleep(0.1)
    print("TxDone flag received")

    # Clear TxDone flag
    write_register(REG_IRQ_FLAGS, 0x08)
    print("TxDone flag cleared")

def check_version():
    version = read_register(REG_VERSION)
    print(f"LoRa Chip Version: {version}")
    if version == 0x12:  # 0x12 è il valore tipico per SX1276/SX1278
        print("Modulo LoRa riconosciuto correttamente.")
    else:
        print("Warning: valore inatteso del registro di versione. Potrebbe esserci un problema di connessione.")


try:
    init_lora()
    check_version()
    while True:
        send_message("Hello World!")
        print("Message sent: Hello World!")
        sleep(5)
except KeyboardInterrupt:
    spi.close()
    