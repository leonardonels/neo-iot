import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep, time

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

# config
PA_OPTIMAL_POWER            = 0x8F
LNA                         = 0x23
PAYLOADLENGHT               = 0x01
PACKET_CONFIG_2             = 0xC3
DIO_MAPPING_RX              = 0x00
DIO_MAPPING_TX              = 0x40

# IRQ masks
IRQ_TX_DONE_MASK            = 0x08
IRQ_PAYLOAD_CRC_ERROR_MASK  = 0x20
IRQ_RX_DONE_MASK            = 0x40

# Var
spi = None
cs_pin = None
reset_pin = None
dio0_pin = None

#include the function lora.set_pins used by the std arduino library for LoRa
def setup(cs_pin_number=25, rst_pin_number=22, dio0_pin_number=27, frequency=8000000):
    global spi, cs_pin, reset_pin, dio0_pin
    
    # Imposta i pin
    cs_pin = OutputDevice(cs_pin_number)
    reset_pin = OutputDevice(rst_pin_number)
    dio0_pin = InputDevice(dio0_pin_number)
    
    # Imposta SPI
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = frequency
    
    # Configura il modulo LoRa
    begin()

def write_register(address, data):
    cs_pin.off()
    spi.writebytes([address | 0x80, data])
    cs_pin.on()
    sleep(0.01)

def read_register(address):
    cs_pin.off()
    spi.writebytes([address & 0x7F])
    response = spi.readbytes(1)
    cs_pin.on()
    return response[0]

def reset_lora():
    reset_pin.off()
    sleep(0.1)
    reset_pin.on()

def begin(frequency=433, hex_bandwidth=0x90, hex_spreading_factor=0x70, hex_coding_rate=0x02, xosc_freq=32):
    reset_lora()
    sleep(0.1)

    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_SLEEP)
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)
    write_register(REG_PA_CONFIG, PA_OPTIMAL_POWER)

    frf = int((frequency * (2**19)) / xosc_freq)
    msb = (frf >> 16) & 0xFF
    mid = (frf >> 8) & 0xFF
    lsb = frf & 0xFF

    write_register(REG_FRF_MSB, msb)
    write_register(REG_FRF_MID, mid)
    write_register(REG_FRF_LSB, lsb)

    write_register(REG_MODEM_CONFIG_1, hex_bandwidth | hex_coding_rate)
    write_register(REG_MODEM_CONFIG_2, hex_spreading_factor)
    write_register(REG_DIO_MAPPING_1, DIO_MAPPING_RX)
    write_register(REG_DETECTION_OPTIMIZE, PACKET_CONFIG_2)
    write_register(REG_LNA, LNA)

def send(message):
    write_register(REG_FIFO_ADDR_PTR, read_register(REG_FIFO_TX_BASE_ADDR))
    for byte in message.encode():
        write_register(REG_FIFO, byte)
    write_register(REG_PAYLOAD_LENGTH, len(message))
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_TX)
    sleep(0.1)
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)

def receive(timeout):
    set_module_on_receive()
    start_time = time()
    while True:
        if dio0_pin.is_active:
            on_receive()
            start_time = time()
        elif time() - start_time > timeout:
            print("Timeout: No messages received within the specified time.")
            write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)
            break
        sleep(0.1)

def set_module_on_receive():
    if read_register(REG_DIO_MAPPING_1) != DIO_MAPPING_RX:
        write_register(REG_DIO_MAPPING_1, DIO_MAPPING_RX)
    write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_CONTINUOUS)
    print("Module set to continuous receive mode")

def on_receive():
    nb_bytes = read_register(REG_RX_NB_BYTES)
    message = [read_register(REG_FIFO) for _ in range(nb_bytes)]
    reconstructed_message = ''.join(chr(byte) for byte in message)
    print(f"Message received: {reconstructed_message}")
    write_register(REG_IRQ_FLAGS, 0xFF)

def close():
    if spi is not None:
        spi.close()
