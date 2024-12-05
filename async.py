import sys
import re
import requests
import LoRa.LoRa as lora
import TinyDB as ty
from LoRa.constants import MODE
from time import time
from datetime import datetime

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


def meteo_tmp():
    url = "https://api.open-meteo.com/v1/forecast?latitude=44.5493&longitude=10.9335&current=temperature_2m,precipitation&timezone=Europe%2FBerlin&forecast_days=1"

    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
                
        current_weather = json_data.get('current_weather', {})
        print(current_weather)
        temperature = current_weather.get('temperature_2m', 'Dati non disponibili')
        precipitation = current_weather.get('precipitation', 'Dati non disponibili')

        print(f"Temperatura: {temperature}°C")
        print(f"Precipitazioni: {precipitation}mm")
    else:
        return False


def button_pressed():
    print("Debug: Interrupt rilevato!")
    message = lora.on_receive()
    print(f'Debug: {message}')
    moisture, index = re.findall(r'\d+', message)
    ty.insert(table, {'index': index, 'moisture': moisture, 'time':datetime.now().strftime("%Y-%m-%dT%H:%M")})

try:
    lora.setup(cs_pin_number=CS_PIN, rst_pin_number=RST_PIN, dio0_pin_number=False, frequency=SPI_FREQUENCY, debug=True)
    lora.begin(frequency=FREQUENCY, hex_bandwidth=BANDWIDTH, hex_spreading_factor=SPREADING_FACTOR, hex_coding_rate=COD_RATE, rx_crc=True)

    ty.createdb('db.json')
    table=ty.createtable('raw_data_test')

    button=lora.async_dio0(DIO0_PIN)
    lora.set_module_on_receive()
    button.when_released = button_pressed

    start = time()
    while True:
        if not abs(start-time())%30:
            ty.printtable(table)


except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    lora.close()