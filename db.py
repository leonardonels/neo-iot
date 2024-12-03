import sys
import LoRa.LoRa as lora
import LoRaTWO.LoRaTWO as loratwo
from LoRa.constants import MODE
from time import sleep, time
from tinydb import TinyDB

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
db = TinyDB('db.json')
test_table = db.table('raw_data_test')
try:
    lora.setup(cs_pin_number=CS_PIN, rst_pin_number=RST_PIN, dio0_pin_number=DIO0_PIN, frequency=SPI_FREQUENCY, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=COD_RATE, rx_crc=True)
    while True:
        message = lora.receive()
        test_table.insert({'name': 'UNO', 'message': message})
        print(message)
        #sleep(0.1)  # Ritardo prima del prossimo controllo

except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    lora.close()

    for sample in test_table.all():
        print(sample)