import LoRa as lora
from time import sleep

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
    lora.set_pins(CS_PIN, RST_PIN, DIO0_PIN)
    lora.set_spi(SPI_FREQUENCY)

    lora.begin()

    #receive(timeout=5)
    packet=0
    while True:
        lora.send(f"{packet}: Hello, world!")
        print(f"{packet}: Hello, world!")
        packet+=1
        sleep(3)

except KeyboardInterrupt:
    #spi.close()
    pass
