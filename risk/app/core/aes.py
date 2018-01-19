#coding:utf-8
from Crypto.Cipher import AES
from Crypto import Random
import base64

class AESHelper:
    def __init__(self, key):
        self.key = key[:16]
        self.BS = AES.block_size
        self.cipher = AES.new(key[:16])

    def pad(self,s):
        return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)

    def unpad(self,s):
        return s[0:-ord(s[-1])]

    def encrypt(self,text):
        encrypted = base64.b64encode(self.cipher.encrypt(self.pad(text))).decode().replace('/','-').replace('=','_')
        return encrypted

    def decrypt(self,text):
        decrypted = self.unpad(self.cipher.decrypt(base64.b64decode(text.replace('_','=').replace('-','/'))))
        return decrypted
