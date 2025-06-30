# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import base64

enc_key = 'ERTISYA##YAZILIM###ERTISYA##YAZILIM'  # 16-chars key


def encrypt_text(data):
    clear_text = str(data)
    clear_text = str.encode(clear_text)

    enc_secret = AES.new(enc_key[:32])
    tag_string = (clear_text +
                  (AES.block_size -
                   len(clear_text) % AES.block_size) * b"\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string)).decode("utf-8")
    return cipher_text


def dencrypt_text(data):
    try:
        dec_secret = AES.new(enc_key[:32])
        raw_decrypted = dec_secret.decrypt(base64.b64decode(data))
        clear_val = raw_decrypted.decode().rstrip("\0")
        return clear_val
    except Exception as e:
        return data