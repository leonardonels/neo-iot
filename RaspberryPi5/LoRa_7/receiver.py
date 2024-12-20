import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep

# Pin configuration
RST_PIN = 22
DIO1_PIN = 23  # Clock for RSSI/sync
DIO2_PIN = 24  # SyncAddr for packet received
CS_PIN = 25

# LoRa register addresses
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_DIO_MAPPING1 = 0x40
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_IRQ_FLAGS = 0x12
REG_VERSION = 0x42
REG_PA_CONFIG = 0x09
REG_MODEM_CONFIG1 = 0x1D
REG_MODEM_CONFIG2 = 0x1E
REG_MODEM_CONFIG3 = 0x26

# Operational modes
MODE_LORA_SLEEP = 0x80
MODE_LORA_STDBY = 0x81
MODE_LORA_RXCONT = 0x85  # RX continua

# LoRa configuration values
MAX_POWER = 0xFF
LOW_POWER = 0x70
BANDWIDTH_500KHZ = 0x72
SPREADING_FACTOR_7 = 0x74
SPREADING_FACTOR_12 = 0xC0  # 1100 0000 in binario per impostare SF a 12
CODING_RATE_4_5 = 0x04

# DIO mapping values
DIO1_MAPPING_RSSI = 0x10  # Mapping for RSSI clock on DIO1
DIO2_MAPPING_SYNCADDR = 0x20  # Mapping for SyncAddr on DIO2

# GPIO setup using gpiozero
reset_pin = OutputDevice(RST_PIN)
dio1_pin = InputDevice(DIO1_PIN)
dio2_pin = InputDevice(DIO2_PIN)
cs_pin = OutputDevice(CS_PIN)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000  # 1 MHz

# Initialize LoRa module
def init_lora():
    check(REG_OP_MODE)
    reset_lora()
    check(REG_OP_MODE)
    write_register(REG_OP_MODE, MODE_LORA_SLEEP)
    check(REG_OP_MODE)
    write_register(REG_OP_MODE, MODE_LORA_STDBY)
    check(REG_OP_MODE)
    write_register(REG_PA_CONFIG, LOW_POWER)
    write_register(REG_MODEM_CONFIG1, BANDWIDTH_500KHZ)
    write_register(REG_MODEM_CONFIG2, SPREADING_FACTOR_12)
    write_register(REG_MODEM_CONFIG3, CODING_RATE_4_5)
    write_register(REG_DIO_MAPPING1, DIO1_MAPPING_RSSI | DIO2_MAPPING_SYNCADDR)
    write_register(REG_FIFO_RX_BASE_ADDR, 0x80)
    print("Module initialized in continuous RX mode.")

# Reset LoRa module
def reset_lora():
    reset_pin.off()
    sleep(0.1)
    reset_pin.on()

# Write to a register
def write_register(address, data):
    cs_pin.off()
    spi.writebytes([address | 0x80, data])
    cs_pin.on()
    sleep(0.01)

# Read from a register
def read_register(address):
    cs_pin.off()
    spi.writebytes([address & 0x7F])
    response = spi.readbytes(1)
    cs_pin.on()
    return response[0]

# Start continuous reception
def receive_message_continuous():
    write_register(REG_OP_MODE, MODE_LORA_RXCONT)
    check(REG_OP_MODE)
    print("Listening for messages in continuous RX mode...")

    while True:
        # Check if SyncAddr is detected (DIO2)
        if dio2_pin.is_active:
            print("SyncAddr detected, receiving packet...")

            # Read packet from FIFO
            payload = []
            while True:
                byte = read_register(REG_FIFO)
                if byte == 0:  # Assuming 0 indicates end of message for simplicity
                    break
                payload.append(chr(byte))

            print("Message received:", ''.join(payload))
            sleep(0.1)  # Short delay before checking for next packet

def check_version():
    version = read_register(REG_VERSION)
    print(f"LoRa Chip Version: {version}")
    if version == 0x12:
        print("LoRa module recognized.")
    else:
        print("Warning: unexpected version. Check connections.")
    
def check(REG):
    current_reg = read_register(REG)
    print(f"Current {REG}: {current_reg}")

try:
    init_lora()
    check_version()
    receive_message_continuous()
except KeyboardInterrupt:
    spi.close()
