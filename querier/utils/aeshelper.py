# coding:utf-8
import sys
import base64
from Crypto.Cipher import AES


class AESHelper:

    def __init__(self, key):
        self.key = key[:16]
        self.BS = AES.block_size
        self.cipher = AES.new(key[:16])

    def pad(self, s):
        bs = self.BS
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def unpad(self, s):
        return s[0:-ord(s[-1])]

    def encrypt(self, text):
        encrypted = base64.b64encode(self.cipher.encrypt(self.pad(text)))
        return encrypted.replace('/', '-').replace('=', '_')

    def decrypt(self, text):
        text = text.replace('_', '=').replace('-', '/')
        return self.unpad(self.cipher.decrypt(base64.b64decode(text)))


if __name__ == '__main__':
    key = sys.argv[1][:16]
    s = sys.argv[2]
    aes = AESHelper(key)
    print s
    if sys.argv[3] == "enc":
        print aes.encrypt(s)
    elif sys.argv[3] == "dec":
        print aes.decrypt(s)
