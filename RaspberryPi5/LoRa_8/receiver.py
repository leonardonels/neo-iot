import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep, time

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

# registers from arduino's LoRa.cpp
REG_FIFO                    = 0x00
REG_OP_MODE                 = 0x01
REG_FRF_MSB                 = 0x06
REG_FRF_MID                 = 0x07
REG_FRF_LSB                 = 0x08
REG_PA_CONFIG               = 0x09
REG_OCP                     = 0x0b
REG_LNA                     = 0x0c
REG_FIFO_ADDR_PTR           = 0x0d
REG_FIFO_TX_BASE_ADDR       = 0x0e
REG_FIFO_RX_BASE_ADDR       = 0x0f
REG_FIFO_RX_CURRENT_ADDR    = 0x10
REG_IRQ_FLAGS               = 0x12
REG_RX_NB_BYTES             = 0x13
REG_PKT_SNR_VALUE           = 0x19
REG_PKT_RSSI_VALUE          = 0x1a
REG_RSSI_VALUE              = 0x1b
REG_MODEM_CONFIG_1          = 0x1d
REG_MODEM_CONFIG_2          = 0x1e
REG_PREAMBLE_MSB            = 0x20
REG_PREAMBLE_LSB            = 0x21
REG_PAYLOAD_LENGTH          = 0x22
REG_MODEM_CONFIG_3          = 0x26
REG_FREQ_ERROR_MSB          = 0x28
REG_FREQ_ERROR_MID          = 0x29
REG_FREQ_ERROR_LSB          = 0x2a
REG_RSSI_WIDEBAND           = 0x2c
REG_DETECTION_OPTIMIZE      = 0x31
REG_INVERTIQ                = 0x33
REG_DETECTION_THRESHOLD     = 0x37
REG_SYNC_WORD               = 0x39
REG_INVERTIQ2               = 0x3b
REG_DIO_MAPPING_1           = 0x40
REG_DIO_MAPPING_2           = 0x41
REG_VERSION                 = 0x42
REG_PA_DAC                  = 0x4d

# modes
MODE_LONG_RANGE_MODE        = 0x80
MODE_SLEEP                  = 0x00
MODE_STDBY                  = 0x01
MODE_TX                     = 0x03
MODE_RX_CONTINUOUS          = 0x05
MODE_RX_SINGLE              = 0x06

# PA config
PA_BOOST                    = 0x80
PA_OPTIMAL_POWER                    = 0x8F

LNA                         = 0x23
MAX_PAYLOADLENGHT           = 0x01
PACKET_CONFIG_2             = 0xC3
DIO_MAPPING_1               = 0x00

# IRQ masks
IRQ_TX_DONE_MASK            = 0x08
IRQ_PAYLOAD_CRC_ERROR_MASK  = 0x20
IRQ_RX_DONE_MASK            = 0x40

RF_MID_BAND_THRESHOLD       = 525E6
RSSI_OFFSET_HF_PORT         = 157
RSSI_OFFSET_LF_PORT         = 164

MAX_PKT_LENGTH              = 255

# GPIO setup using gpiozero
def set_pins(CS_PIN, RST_PIN, DIO0_PIN):
    NSS = OutputDevice(CS_PIN)
    RST = OutputDevice(RST_PIN)
    DIO0 = InputDevice(DIO0_PIN)
    return NSS, RST, DIO0

# SPI setup
def set_spi(frequency):
    spi=spidev.SpiDev()
    spi.open(0,0)
    spi.max_speed_hz = frequency
    return spi

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

# Reset LoRa module
def reset_lora():
    reset_pin.off()
    sleep(0.1)
    reset_pin.on()

# Initialize LoRa module
def begin():
    reset_lora()
    sleep(0.1)

    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_SLEEP)
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)

    write_register(REG_PA_CONFIG, PA_OPTIMAL_POWER)

    frf = int((FREQUENCY*(2**19))/F_XOSC)
    print(f"FRF (DEC): {frf}")
    print(f"FRF (HEX): {hex(frf)}")    
    msb = (frf >> 16) & 0xFF   # RegFrfMsb
    mid = (frf >> 8) & 0xFF    # RegFrfMid
    lsb = frf & 0xFF           # RegFrfLsb
    print(f"RegFrfMsb (MSB): {msb} DEC), {hex(msb)} (HEX)")
    print(f"RegFrfMid (MID): {mid} (DEC), {hex(mid)} (HEX)")
    print(f"RegFrfLsb (LSB): {lsb} (DEC), {hex(lsb)} (HEX)")

    write_register(REG_FRF_MSB, msb)
    write_register(REG_FRF_MID, mid)
    write_register(REG_FRF_LSB, lsb)

    write_register(REG_MODEM_CONFIG_1, BANDWIDTH | CODING_RATE)
    write_register(REG_MODEM_CONFIG_2, SPREADING_FACTOR)

    write_register(REG_DIO_MAPPING_1, DIO_MAPPING_1)
    write_register(REG_DETECTION_OPTIMIZE, PACKET_CONFIG_2)
    write_register(REG_LNA, LNA)

def check(REG):
    return read_register(REG)

# Imposta il modulo in modalità ricezione continua
def set_module_on_receive():
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_CONTINUOUS)
    print("Module set to continuous receive mode")

# Funzione per gestire la ricezione di un messaggio
def on_receive():
    # Legge il numero di byte ricevuti
    nb_bytes = read_register(REG_RX_NB_BYTES)
    print(f"Received {nb_bytes} bytes")

    # Leggi il messaggio dal registro FIFO
    message = []
    for _ in range(nb_bytes):
        message.append(read_register(REG_FIFO))

    # Ricostruire il messaggio in una stringa (se i dati sono ASCII)
    reconstructed_message = ''.join(chr(byte) for byte in message)
    print(f"Message received: {reconstructed_message}")

    # Ripulisci il buffer (resetta il registro IRQ)
    write_register(REG_IRQ_FLAGS, 0xFF)  # Resetta tutti i flag di interrupt

def receive(timeout=5):
    set_module_on_receive()
    print(f"Waiting for messages...")

    start_time = time()  # Registra il tempo di inizio
    while True:
        if dio0_pin.is_active:  # Controlla se DIO0 è attivo
            on_receive()  # Gestisci la ricezione del messaggio
            break  # Esci dal ciclo dopo aver ricevuto il messaggio
        elif time() - start_time > timeout:  # Controlla il timeout
            print("Timeout: No messages received within the specified time.")
            break  # Esci dal ciclo in caso di timeout
        sleep(0.1)  # Aspetta un attimo prima di controllare di nuovo

try:
    cs_pin, reset_pin, dio0_pin = set_pins(CS_PIN, RST_PIN, DIO0_PIN)
    spi = set_spi(SPI_FREQUENCY)

    begin()
    print(f"Module initiated with mode {check(REG_OP_MODE)}")

    receive()

except KeyboardInterrupt:
    spi.close()
