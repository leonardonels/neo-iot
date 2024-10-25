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
REG_VERSION = 0x42

# LoRa operational modes
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x83
MODE_LORA = 0x80

# LoRa configuration values
MAX_POWER = 0xF0
BANDWIDTH_500KHZ = 0x72
SPREADING_FACTOR_7 = 0x74
CODING_RATE_4_5 = 0x04

# MSB settings
MSB_1 = 0x80
MSB_0 = 0x7F

# GPIO setup using gpiozero
reset_pin = OutputDevice(RST_PIN, active_high=False)
dio0_pin = InputDevice(DIO0_PIN)
cs_pin = OutputDevice(CS_PIN, active_high=False)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000

# Function to write on LoRa register
def write_register(address, data):
    cs_pin.on()
    spi.xfer([address | MSB_1, data])
    cs_pin.off()

# Function to read from LoRa register
def read_register(address):
    cs_pin.on()
    response = spi.xfer([address & MSB_0, 0x00])
    cs_pin.off()
    return response[1]

# Reset LoRa module
def reset_lora():
    reset_pin.on()
    sleep(0.1)
    reset_pin.off()
    sleep(0.1)

# Initialize LoRa transmitter
def init_lora():
    reset_lora()
    write_register(REG_OP_MODE, MODE_LORA | MODE_STDBY)
    write_register(REG_PA_CONFIG, MAX_POWER)
    write_register(REG_MODEM_CONFIG1, BANDWIDTH_500KHZ)
    write_register(REG_MODEM_CONFIG2, SPREADING_FACTOR_7)
    write_register(REG_MODEM_CONFIG3, CODING_RATE_4_5)
    write_register(REG_FIFO_TX_BASE_ADDR, 0x80)
    write_register(REG_FIFO_RX_BASE_ADDR, 0x80)
    print("Module initialized.")

# Send a message
def send_message(message):
    write_register(REG_OP_MODE, MODE_LORA | MODE_TX)
    write_register(REG_FIFO_ADDR_PTR, 0x80)
    for byte in message.encode():
        write_register(REG_FIFO, byte)
    write_register(REG_PAYLOAD_LENGTH, len(message))
    write_register(REG_OP_MODE, MODE_LORA | MODE_TX)
    print("Message wronte")

    while not dio0_pin.is_active:
        sleep(0.1)

    write_register(REG_IRQ_FLAGS, 0x08)
    print("Message sent")

try:
    init_lora()
    while True:
        send_message("Hello World!")
        print("Message sent: Hello World!")
        sleep(5)
except KeyboardInterrupt:
    spi.close()
