import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ReportEncryptor:

    def __init__(self):

        key = os.getenv("BUG_BOUNTY_KEY")

        if not key:
            raise Exception(
                "BUG_BOUNTY_KEY missing in environment"
            )

        self.key = base64.b64decode(key)

        if len(self.key) != 32:
            raise Exception(
                "BUG_BOUNTY_KEY must be 32 bytes"
            )

        self.aes = AESGCM(self.key)


    def encrypt(self, data: str):

        nonce = os.urandom(12)

        encrypted = self.aes.encrypt(
            nonce,
            data.encode(),
            None
        )

        return {
            "nonce": base64.b64encode(nonce).decode(),
            "data": base64.b64encode(encrypted).decode()
        }


    def decrypt(self, payload):

        nonce = base64.b64decode(
            payload["nonce"]
        )

        data = base64.b64decode(
            payload["data"]
        )

        decrypted = self.aes.decrypt(
            nonce,
            data,
            None
        )

        return decrypted.decode()
