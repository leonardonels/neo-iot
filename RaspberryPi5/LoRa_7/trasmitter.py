import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep

# Pin configuration
RST_PIN = 22
DIO0_PIN = 27
CS_PIN = 25

# LoRa register addresses (consts)
REG_OP_MODE = 0x01
REG_PA_CONFIG = 0x09

# LoRa configuration values
MAX_POWER = 0xFF

# LoRa operational modes
MODE_LORA_SLEEP = 0x80
MODE_LORA_STDBY = 0x81
MODE_LORA_TX = 0x83
MODE_LORA = 0x80

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
spi.max_speed_hz = 5000000  # 5 MHz

# Reset LoRa module
def reset_lora():
    reset_pin.on()
    sleep(0.1)
    reset_pin.off()
    sleep(0.1)

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

def check_mode():
    current_mode = read_register(REG_OP_MODE)
    print(f"Current mode: {current_mode}")

#...

def init_lora():
    reset_lora()
    write_register(REG_OP_MODE, MODE_LORA_STDBY)
    write_register(REG_PA_CONFIG, MAX_POWER)

try:
    
    while True:
        sleep(5)  # Keep checking mode every 5 seconds
except KeyboardInterrupt:
    spi.close()
    