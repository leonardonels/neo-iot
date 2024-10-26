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
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_PAYLOAD_LENGTH = 0x22
REG_IRQ_FLAGS = 0x12
REG_DIO_MAPPING1 = 0x40

REG_VERSION = 0x42  # Registro della versione del chip

# LoRa configuration values
MAX_POWER = 0xFF
LOW_POWER = 0x70
BANDWIDTH_500KHZ = 0x72
SPREADING_FACTOR_7 = 0x74
CODING_RATE_4_5 = 0x04
DIO0_MAPPING_RXDONE = 0x00  # Mappa RxDone su DIO0

# LoRa operational modes
MODE_LORA_SLEEP = 0x80
MODE_LORA_STDBY = 0x81
MODE_LORA_RXCONT = 0x85  # RX continua

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

# Initialize LoRa module
def init_lora():
    reset_lora()
    write_register(REG_OP_MODE, MODE_LORA_SLEEP)
    check(REG_OP_MODE)
    write_register(REG_OP_MODE, MODE_LORA_STDBY)
    check(REG_OP_MODE)
    write_register(REG_DIO_MAPPING1, DIO0_MAPPING_RXDONE)
    check(REG_DIO_MAPPING1)
    write_register(REG_PA_CONFIG, LOW_POWER)
    write_register(REG_MODEM_CONFIG1, BANDWIDTH_500KHZ)
    write_register(REG_MODEM_CONFIG2, SPREADING_FACTOR_7)
    write_register(REG_MODEM_CONFIG3, CODING_RATE_4_5)
    write_register(REG_FIFO_RX_BASE_ADDR, 0x80)
    print("Module initialized and ready for RX.")

# Reset LoRa module
def reset_lora():
    sleep(0.1)
    reset_pin.off()
    sleep(0.1)
    reset_pin.on()

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

def check(REG):
    current_reg = read_register(REG)
    print(f"Current {REG}: {current_reg}")

# Receive a message
def receive_message():
    write_register(REG_OP_MODE, MODE_LORA_RXCONT)  # Set to RX continuous mode
    print("Listening for messages...")

    while True:
        if dio0_pin.is_active:  # Check if RxDone flag is set
            print("Packet received!")
            
            # Clear RxDone flag
            write_register(REG_IRQ_FLAGS, 0x40)

            # Read packet from FIFO
            payload = []
            while True:
                byte = read_register(REG_FIFO)
                if byte == 0:  # Assuming 0 indicates end of message for simplicity
                    break
                payload.append(chr(byte))

            print("Message received:", ''.join(payload))
            break
        sleep(0.1)

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
    receive_message()  # Ascolta continuamente per i messaggi
except KeyboardInterrupt:
    spi.close()
