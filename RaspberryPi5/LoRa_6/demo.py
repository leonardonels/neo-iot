import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep

# Pin configuration
RST_PIN = 22
DIO0_PIN = 27
CS_PIN = 25

# LoRa register addresses (consts)
REG_OP_MODE = 0x01

# LoRa operational modes
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x03
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
spi.max_speed_hz = 500000   #500Hz

#...
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

try:
    while True:
        print("starting demo")
        write_register(REG_OP_MODE, MODE_LORA)
        check_mode()
except KeyboardInterrupt:
    spi.close()