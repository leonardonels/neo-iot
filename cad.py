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

# Main
try:
    lora.setup(CS_PIN, RST_PIN, DIO0_PIN, SPI_FREQUENCY, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=COD_RATE, rx_crc=True)
    while True:
        cad=lora.activity_derection(read=True)
        if cad==0:
            print("Canale inattivo.")
        elif cad ==-1:
            print("error on activity detection!")
        else:
            print(cad)
        sleep(0.01)  # Ritardo prima del prossimo controllo

except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    lora.close()