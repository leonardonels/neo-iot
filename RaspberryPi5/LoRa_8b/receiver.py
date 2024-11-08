import LoRa as lora

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
CODING_RATE                 = 0x02 # 4/5

try:
    lora.setup(CS_PIN, RST_PIN, DIO0_PIN, SPI_FREQUENCY)

    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=CODING_RATE)

    while True:
        lora.receive(timeout=30)

except KeyboardInterrupt:
    lora.close()
