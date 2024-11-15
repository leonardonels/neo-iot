from time import sleep
from LoRa.constants import MODE, REG
import LoRa.LoRa as lora
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from os import urandom


# AES 128
def send(message, key):

    padder = PKCS7(128).padder()
    padded_message = padder.update(message.encode('utf-8')) + padder.finalize()

    iv = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()
    lora.send(iv+ciphertext)