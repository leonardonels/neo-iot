import spidev
from gpiozero import OutputDevice, InputDevice
from time import sleep, time
from LoRa.constants import REG, MODE

# Var
debugger = None
spi = None
cs_pin = None
reset_pin = None
dio0_pin = None

#include the function lora.set_pins used by the std arduino library for LoRa
def setup(cs_pin_number=25, rst_pin_number=22, dio0_pin_number=27, frequency=8000000, debug=False):
    global debugger, spi, cs_pin, reset_pin, dio0_pin

    #set debug mode
    debugger = debug
    
    # Imposta i pin
    cs_pin = OutputDevice(cs_pin_number)
    reset_pin = OutputDevice(rst_pin_number)
    dio0_pin = InputDevice(dio0_pin_number)
    
    # Imposta SPI
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = frequency

def set_mode(mode):
    write_register(REG.LORA.OP_MODE, mode)

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

def begin(frequency=433, hex_bandwidth=0x90, hex_spreading_factor=0x70, hex_coding_rate=0x02, rx_crc=False, xosc_freq=32):
    reset_lora()
    sleep(0.1)

    write_register(REG.LORA.OP_MODE, MODE.SLEEP)
    while read_register(REG.LORA.OP_MODE)!=MODE.SLEEP:
        print("Error initiating the LoRa module, wait...")
        sleep(5)
        write_register(REG.LORA.OP_MODE, MODE.SLEEP)
    write_register(REG.LORA.OP_MODE, MODE.STDBY)
    if(debugger):print(f"BEGIN_OP_MODE: {read_register(REG.LORA.OP_MODE)}")
    write_register(REG.LORA.PA_CONFIG, 0xFF)

    frf = int((frequency * (2**19)) / xosc_freq)
    msb = (frf >> 16) & 0xFF
    mid = (frf >> 8) & 0xFF
    lsb = frf & 0xFF

    write_register(REG.LORA.FR_MSB, msb)
    write_register(REG.LORA.FR_MID, mid)
    write_register(REG.LORA.FR_LSB, lsb)

    write_register(REG.LORA.MODEM_CONFIG_1, hex_bandwidth | hex_coding_rate)
    write_register(REG.LORA.MODEM_CONFIG_2, hex_spreading_factor | 0x04*rx_crc)
    write_register(REG.LORA.DIO_MAPPING_1, 0x00) #DIO_MAPPING_RX
    write_register(REG.LORA.DETECT_OPTIMIZE, 0x83)
    write_register(REG.LORA.LNA, 0x23)
    sleep(1)

def send_bytes(byte_message):
    write_register(REG.LORA.FIFO_ADDR_PTR, read_register(REG.LORA.FIFO_TX_BASE_ADDR))
    for byte in byte_message:
        write_register(REG.LORA.FIFO, byte)
    write_register(REG.LORA.PAYLOAD_LENGTH, len(byte_message))
    write_register(REG.LORA.OP_MODE, MODE.TX)
    if(debugger):print(f"SEND_OP_MODE: {read_register(REG.LORA.OP_MODE)}")

def send(message):
    write_register(REG.LORA.FIFO_ADDR_PTR, read_register(REG.LORA.FIFO_TX_BASE_ADDR))
    for byte in message.encode():
        write_register(REG.LORA.FIFO, byte)
    write_register(REG.LORA.PAYLOAD_LENGTH, len(message))
    write_register(REG.LORA.OP_MODE, MODE.TX)
    if(debugger):print(f"SEND_OP_MODE: {read_register(REG.LORA.OP_MODE)}")
    print(f"{message} sent.")

def activity_derection(timeout=0):
    start_time = time()
    while True:
        if read_register(REG.LORA.IRQ_FLAGS)&4==4:
            write_register(REG.LORA.IRQ_FLAGS, 0x04)
        if read_register(REG.LORA.IRQ_FLAGS)&1==1:
            write_register(REG.LORA.IRQ_FLAGS, 0x01)
        #print(read_register(REG.LORA.IRQ_FLAGS))
        write_register(REG.LORA.OP_MODE, MODE.CAD)
        write_register(REG.LORA.OP_MODE, MODE.RXCONT)
        if read_register(REG.LORA.IRQ_FLAGS)&5 == 5:
            print("preamble detected...")
            return True
        if (time() - start_time > timeout)&(timeout!=0):
            write_register(REG.LORA.OP_MODE, MODE.STDBY)
            return False
        
def single_receive():
    write_register(REG.LORA.FIFO_ADDR_PTR, read_register(REG.LORA.FIFO_RX_BASE_ADDR))
    start_time = time()
    while True:
        if dio0_pin.is_active:
            nb_bytes = read_register(REG.LORA.RX_NB_BYTES)
            message = [read_register(REG.LORA.FIFO) for _ in range(nb_bytes)]
            reconstructed_message = ''.join(chr(byte) for byte in message)
            #print(f"Message received: {reconstructed_message}")
            write_register(REG.LORA.OP_MODE, MODE.STDBY)
            return reconstructed_message
        elif time() - start_time > 7:
            write_register(REG.LORA.OP_MODE, MODE.STDBY)
            return "Timeout: No messages received within the specified time."

def receive(timeout=5):
    set_module_on_receive()
    start_time = time()
    while True:
        if dio0_pin.is_active:
            message = on_receive()
            start_time = time()
            return message
        elif time() - start_time > timeout:
            write_register(REG.LORA.OP_MODE, MODE.STDBY)
            return "Timeout: No messages received within the specified time."

def set_module_on_receive():
    if read_register(REG.LORA.DIO_MAPPING_1) != 0x00:
        write_register(REG.LORA.DIO_MAPPING_1, 0x00)
    write_register(REG.LORA.OP_MODE, MODE.RXCONT)
    write_register(REG.LORA.FIFO_ADDR_PTR, read_register(REG.LORA.FIFO_RX_BASE_ADDR))
    print("Debug: Module set to continuous receive mode")

def on_receive():
    nb_bytes = read_register(REG.LORA.RX_NB_BYTES)
    message = [read_register(REG.LORA.FIFO) for _ in range(nb_bytes)]
    reconstructed_message = ''.join(chr(byte) for byte in message)
    #print(f"Message received: {reconstructed_message}")
    write_register(REG.LORA.OP_MODE, MODE.STDBY)
    write_register(REG.LORA.OP_MODE, MODE.RXCONT)
    write_register(REG.LORA.FIFO_ADDR_PTR, read_register(REG.LORA.FIFO_RX_BASE_ADDR))
    write_register(REG.LORA.IRQ_FLAGS, 0xFF)
    return reconstructed_message

def close():
    if spi is not None:
        spi.close()