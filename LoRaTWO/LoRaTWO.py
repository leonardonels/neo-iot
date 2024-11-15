from time import sleep
from LoRa.constants import MODE, REG
import LoRa.LoRa as lora
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom


# AES 128
def send(message, key):

    iv = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
    lora.send(iv+ciphertext)