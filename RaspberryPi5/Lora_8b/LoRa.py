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

class LoRa:
    def __init__(self, cs_pin=25, rst_pin=22, dio0_pin=27, frequency=8000000):
        # Configurazioni iniziali
        self.CS_PIN = cs_pin
        self.RST_PIN = rst_pin
        self.DIO0_PIN = dio0_pin
        self.SPI_FREQUENCY = frequency

        # Impostazioni GPIO e SPI
        self.cs_pin, self.reset_pin, self.dio0_pin = self.set_pins()
        self.spi = self.set_spi()

        # Configura il modulo LoRa
        self.begin()

    def set_pins(self):
        NSS = OutputDevice(self.CS_PIN)
        RST = OutputDevice(self.RST_PIN)
        DIO0 = InputDevice(self.DIO0_PIN)
        return NSS, RST, DIO0

    def set_spi(self):
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = self.SPI_FREQUENCY
        return spi

    def write_register(self, address, data):
        self.cs_pin.off()
        self.spi.writebytes([address | 0x80, data])
        self.cs_pin.on()
        sleep(0.01)

    def read_register(self, address):
        self.cs_pin.off()
        self.spi.writebytes([address & 0x7F])
        response = self.spi.readbytes(1)
        self.cs_pin.on()
        return response[0]

    def reset_lora(self):
        self.reset_pin.off()
        sleep(0.1)
        self.reset_pin.on()

    def begin(self, frequency=433, hex_bandwidth=0x90, hex_spreading_factor=0x70,hex_coding_rate=0x02, xosc_freq=32):
        self.reset_lora()
        sleep(0.1)

        self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_SLEEP)
        self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)

        self.write_register(REG_PA_CONFIG, PA_OPTIMAL_POWER)

        frf = int((frequency*(2**19))/xosc_freq)
        print(f"FRF (DEC): {frf}")
        print(f"FRF (HEX): {hex(frf)}")    
        msb = (frf >> 16) & 0xFF   # RegFrfMsb
        mid = (frf >> 8) & 0xFF    # RegFrfMid
        lsb = frf & 0xFF           # RegFrfLsb
        print(f"RegFrfMsb (MSB): {msb} DEC), {hex(msb)} (HEX)")
        print(f"RegFrfMid (MID): {mid} (DEC), {hex(mid)} (HEX)")
        print(f"RegFrfLsb (LSB): {lsb} (DEC), {hex(lsb)} (HEX)")

        self.write_register(REG_FRF_MSB, msb)
        self.write_register(REG_FRF_MID, mid)
        self.write_register(REG_FRF_LSB, lsb)

        self.write_register(REG_MODEM_CONFIG_1, hex_bandwidth | hex_coding_rate)
        self.write_register(REG_MODEM_CONFIG_2, hex_spreading_factor)

        self.write_register(REG_DIO_MAPPING_1, DIO_MAPPING_RX)   # 0x00
        self.write_register(REG_DETECTION_OPTIMIZE, PACKET_CONFIG_2)
        self.write_register(REG_LNA, LNA)

    def check(self, REG):
        return self.read_register(REG)

    def set_module_on_receive(self):
        # Imposta il modulo in modalità ricezione
        if self.check(REG_DIO_MAPPING_1) != DIO_MAPPING_RX:
            self.write_register(REG_DIO_MAPPING_1, DIO_MAPPING_RX)
        self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_CONTINUOUS)
        print("Module set to continuous receive mode")

    def on_receive(self):
        # Funzione per gestire la ricezione
        nb_bytes = self.read_register(REG_RX_NB_BYTES)
        message = [self.read_register(REG_FIFO) for _ in range(nb_bytes)]
        reconstructed_message = ''.join(chr(byte) for byte in message)
        print(f"Message received: {reconstructed_message}")
        self.write_register(REG_IRQ_FLAGS, 0xFF)

    def receive(self, timeout):
        self.set_module_on_receive()
        start_time = time()
        while True:
            if self.dio0_pin.is_active:
                self.on_receive()
                start_time = time()
            elif time() - start_time > timeout:
                print("Timeout: No messages received within the specified time.")
                self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)
                break
            sleep(0.1)

    def send(self, message):
        # Funzione per inviare un messaggio
        self.write_register(REG_FIFO_ADDR_PTR, self.read_register(REG_FIFO_TX_BASE_ADDR))
        for byte in message.encode():
            self.write_register(REG_FIFO, byte)
        self.write_register(REG_PAYLOAD_LENGTH, len(message))
        self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_TX)
        sleep(0.1)
        self.write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)

    def close(self):
        self.spi.close()
