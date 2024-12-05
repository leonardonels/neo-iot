import sys
import LoRa.LoRa as lora
import LoRaTWO.LoRaTWO as loratwo
from LoRa.constants import MODE
from time import sleep
from signal import pause

# Pin configuration
RST_PIN                     = 22
DIO0_PIN                    = 27
CS_PIN                      = 25

#SPI configuration
SPI_FREQUENCY               = 8000000 # 8 MHz

#LoRa configuration
FREQUENCY                   = 433  # MHz
F_XOSC                      = 32   # MHz
BANDWIDTH                   = 0x90 # 500 Hz
SPREADING_FACTOR            = 0x70 # 7
COD_RATE                    = 0x02 # 4/5


def button_pressed():
    print("Interrupt rilevato!")
    print(lora.on_receive)

try:
    lora.setup(cs_pin_number=CS_PIN, rst_pin_number=RST_PIN, dio0_pin_number=False, frequency=SPI_FREQUENCY, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=COD_RATE, rx_crc=True)

    button=lora.async_dio0(DIO0_PIN)
    lora.set_module_on_receive()
    button.when_pressed = button_pressed

    while True:
        pass
        
except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    lora.close()