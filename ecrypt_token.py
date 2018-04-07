#!/usr/bin/python3

import aes
import getpass

token = input('token: ')
key = getpass.getpass(prompt='Password:')
filename = input('Filename: ')

cipher = aes.AESCipher(key=key)
ss = cipher.encrypt(token)

f = open(filename, 'w')
f.write(ss)

f.close()

print('Ecrypted token was written to', filename)

