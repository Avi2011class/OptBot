#!/usr/bin/python3

import aes
import getpass
import sys


class Encryptor:

    @staticmethod
    def encrypt_and_save(token, key, filename):
        cipher = aes.AESCipher(key=key)
        encrypted_token = cipher.encrypt(token)
        f = open(filename, 'w')
        f.write(encrypted_token)
        f.close()

    @staticmethod
    def decrypt_and_return(key, filename):
        cipher = aes.AESCipher(key=key)
        encrypted_token = open(filename, 'r').read()
        token = cipher.decrypt(encrypted_token)
        return token


if __name__ == "__main__":
    if not '-d' in sys.argv:
        print("Encryption mode")
        Encryptor.encrypt_and_save(input('Token: '),
                                   getpass.getpass(prompt='Password: '),
                                   input('Filename: '))
    else:
        print("Decryption mode")
        print(Encryptor.decrypt_and_return(getpass.getpass(prompt='Password: '),
                                           input('Filename: ')))
