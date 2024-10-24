import time
from SX127x.LoRa import *
from SX127x.board_config import BOARD

class LoRaReceiver(LoRa):
    def __init__(self):
        super(LoRaReceiver, self).__init__(verbose=False)
        BOARD.setup()

    def start(self):
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.set_freq(433.0)  # Frequenza in MHz
        self.set_bw(500)  # Larghezza di banda a 500kHz
        self.set_spreading_factor(7)  # SF7
        self.set_coding_rate(4, 5)  # CR 4/5
        self.set_rx_crc(True)  # Abilita il controllo CRC
        self.set_mode(MODE.RXCONT)  # Modalità di ricezione continua

    def on_rx_done(self):
        print("Messaggio ricevuto!")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print("Payload:", bytes(payload).decode('utf-8', errors='ignore'))
        self.set_mode(MODE.RXCONT)  # Continua la ricezione

if __name__ == "__main__":
    receiver = LoRaReceiver()
    receiver.start()
    print("In ascolto per i messaggi LoRa...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interruzione del programma.")
    finally:
        receiver.set_mode(MODE.SLEEP)
        BOARD.teardown()
