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
    lora.send_bytes(iv+ciphertext)
    print(f"{message} sent.")

def receive(timeout, key):
    encrypted_data = lora.receive(timeout)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data.decode('utf-8')