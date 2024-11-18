import sys
import LoRa.LoRa as lora
import LoRaTWO.LoRaTWO as loratwo
from LoRa.constants import MODE
from time import sleep

# Pin configuration
RST_PIN                     = 22
DIO0_PIN                    = 27
DIO1_PIN                    = 24
CS_PIN                      = 25

#SPI configuration
SPI_FREQUENCY               = 8000000 # 8 MHz

#LoRa configuration
FREQUENCY                   = 433  # MHz
F_XOSC                      = 32   # MHz
BANDWIDTH                   = 0x90 # 500 Hz
SPREADING_FACTOR            = 0x70 # 7
COD_RATE                    = 0x02 # 4/5

# Init
devaddr = [0x26, 0x01, 0x11, 0x5F]
key = bytes([0xC3, 0x24, 0x64, 0x98, 0xDE, 0x56, 0x5D, 0x8C, 0x55, 0x88, 0x7C, 0x05, 0x86, 0xF9, 0x82, 0x26])
appskey = [0x15, 0xF6, 0xF4, 0xD4, 0x2A, 0x95, 0xB0, 0x97, 0x53, 0x27, 0xB7, 0xC1, 0x45, 0x6E, 0xC5, 0x45]


try:
    lora.setup(CS_PIN, RST_PIN, DIO0_PIN, SPI_FREQUENCY, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=COD_RATE, rx_crc=True)

    while True:
        #message = loratwo.receive(timeout=5, key=key)
        message = lora.receive(timeout=5)
        print(message)
        sleep(1)
except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    lora.close()