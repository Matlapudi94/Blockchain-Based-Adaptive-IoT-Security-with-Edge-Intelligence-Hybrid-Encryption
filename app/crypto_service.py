from __future__ import annotations

import base64
import json
import os
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from phe import paillier


class CryptoService:
    def __init__(self) -> None:
        self._aes_key = AESGCM.generate_key(bit_length=256)
        self._aesgcm = AESGCM(self._aes_key)
        self._light_key = ChaCha20Poly1305.generate_key()
        self._chacha = ChaCha20Poly1305(self._light_key)
        self._phe_public_key, self._phe_private_key = paillier.generate_paillier_keypair()

    def encrypt(self, payload: dict[str, Any], mode: str) -> tuple[bytes, dict[str, Any]]:
        if mode == "AES_FULL":
            return self._encrypt_aes(payload), {"mode": mode}
        if mode == "AES_PHE":
            transformed = self._apply_phe(payload)
            return self._encrypt_aes(transformed), {"mode": mode, "phe_fields": self._numeric_fields(payload)}
        if mode == "AES_MASK":
            transformed = self._mask_fields(payload)
            return self._encrypt_aes(transformed), {"mode": mode, "masked": True}
        if mode == "LIGHTWEIGHT":
            return self._encrypt_lightweight(payload), {"mode": mode}
        plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
        return plaintext, {"mode": mode}

    def decrypt(self, ciphertext: bytes, mode: str) -> dict[str, Any]:
        if mode == "AES_FULL":
            return self._decrypt_aes(ciphertext)
        if mode == "AES_PHE":
            transformed = self._decrypt_aes(ciphertext)
            return self._decrypt_phe_payload(transformed)
        if mode == "AES_MASK":
            return self._decrypt_aes(ciphertext)
        if mode == "LIGHTWEIGHT":
            return self._decrypt_lightweight(ciphertext)
        return json.loads(ciphertext.decode("utf-8"))

    def _encrypt_aes(self, payload: dict[str, Any]) -> bytes:
        nonce = os.urandom(12)
        plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
        return nonce + self._aesgcm.encrypt(nonce, plaintext, None)

    def _decrypt_aes(self, ciphertext: bytes) -> dict[str, Any]:
        nonce = ciphertext[:12]
        body = ciphertext[12:]
        plaintext = self._aesgcm.decrypt(nonce, body, None)
        return json.loads(plaintext.decode("utf-8"))

    def _encrypt_lightweight(self, payload: dict[str, Any]) -> bytes:
        nonce = os.urandom(12)
        plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
        return nonce + self._chacha.encrypt(nonce, plaintext, None)

    def _decrypt_lightweight(self, ciphertext: bytes) -> dict[str, Any]:
        nonce = ciphertext[:12]
        body = ciphertext[12:]
        plaintext = self._chacha.decrypt(nonce, body, None)
        return json.loads(plaintext.decode("utf-8"))

    def _apply_phe(self, payload: dict[str, Any]) -> dict[str, Any]:
        transformed: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)):
                encrypted_number = self._phe_public_key.encrypt(value)
                transformed[key] = {
                    "phe_ciphertext": str(encrypted_number.ciphertext()),
                    "phe_exponent": encrypted_number.exponent,
                }
            else:
                transformed[key] = value
        return transformed

    def _decrypt_phe_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        decrypted: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, dict) and "phe_ciphertext" in value and "phe_exponent" in value:
                encrypted_number = paillier.EncryptedNumber(
                    self._phe_public_key,
                    int(value["phe_ciphertext"]),
                    int(value["phe_exponent"]),
                )
                decrypted[key] = self._phe_private_key.decrypt(encrypted_number)
            else:
                decrypted[key] = value
        return decrypted

    def _numeric_fields(self, payload: dict[str, Any]) -> list[str]:
        return [key for key, value in payload.items() if isinstance(value, (int, float))]

    def _mask_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        masked: dict[str, Any] = {}
        for key, value in payload.items():
            if "id" in key.lower() and isinstance(value, str):
                masked[key] = value[:2] + "*" * max(0, len(value) - 2)
            else:
                masked[key] = value
        return masked

    @staticmethod
    def encode_ciphertext(ciphertext: bytes) -> str:
        return base64.b64encode(ciphertext).decode("utf-8")

    @staticmethod
    def decode_ciphertext(ciphertext_b64: str) -> bytes:
        return base64.b64decode(ciphertext_b64.encode("utf-8"))
