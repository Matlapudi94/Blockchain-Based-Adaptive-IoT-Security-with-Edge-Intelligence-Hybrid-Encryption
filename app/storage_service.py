from __future__ import annotations

import json
from io import BytesIO

from pymongo import MongoClient
import requests

from app.config import settings
from app.crypto_service import CryptoService
from app.models import StoredObject


class StorageService:
    def __init__(self) -> None:
        self.mongo = MongoClient(settings.mongo_uri)
        self.collection = self.mongo[settings.mongo_db][settings.mongo_collection]
        self.ipfs_api = self._normalize_ipfs_api(settings.ipfs_addr)

    def store(self, data_id: str, ciphertext: bytes, metadata: dict, storage_kind: str) -> StoredObject:
        ciphertext_b64 = CryptoService.encode_ciphertext(ciphertext)
        if storage_kind == "IPFS":
            payload = {
                "data_id": data_id,
                "ciphertext": ciphertext_b64,
                "metadata": metadata,
                "storage_kind": storage_kind,
            }
            cid = self._ipfs_add_bytes(json.dumps(payload, sort_keys=True).encode("utf-8"))
            return StoredObject(
                data_id=data_id,
                storage_ref=f"ipfs://{cid}",
                storage_kind=storage_kind,
                ciphertext=ciphertext,
                metadata=metadata,
            )

        self.collection.replace_one(
            {"_id": data_id},
            {
                "_id": data_id,
                "ciphertext": ciphertext_b64,
                "metadata": metadata,
                "storage_kind": storage_kind,
            },
            upsert=True,
        )
        return StoredObject(
            data_id=data_id,
            storage_ref=f"mongodb://{data_id}",
            storage_kind=storage_kind,
            ciphertext=ciphertext,
            metadata=metadata,
        )

    def retrieve(self, storage_ref: str, storage_kind: str) -> StoredObject:
        if storage_kind == "IPFS":
            cid = storage_ref.replace("ipfs://", "", 1)
            payload = json.loads(self._ipfs_cat(cid).decode("utf-8"))
            return StoredObject(
                data_id=payload["data_id"],
                storage_ref=storage_ref,
                storage_kind=storage_kind,
                ciphertext=CryptoService.decode_ciphertext(payload["ciphertext"]),
                metadata=payload["metadata"],
            )

        data_id = storage_ref.replace("mongodb://", "", 1)
        doc = self.collection.find_one({"_id": data_id})
        if not doc:
            raise KeyError(f"No MongoDB record found for {data_id}")
        return StoredObject(
            data_id=data_id,
            storage_ref=storage_ref,
            storage_kind=storage_kind,
            ciphertext=CryptoService.decode_ciphertext(doc["ciphertext"]),
            metadata=doc["metadata"],
        )

    def tamper(self, storage_ref: str, storage_kind: str) -> None:
        if storage_kind == "IPFS":
            raise ValueError("Tampering demo currently supports MongoDB-backed records only.")

        data_id = storage_ref.replace("mongodb://", "", 1)
        doc = self.collection.find_one({"_id": data_id})
        if not doc:
            raise KeyError(f"No MongoDB record found for {data_id}")

        ciphertext = CryptoService.decode_ciphertext(doc["ciphertext"])
        tampered = ciphertext[:-1] + (b"0" if ciphertext[-1:] != b"0" else b"1")
        self.collection.update_one(
            {"_id": data_id},
            {"$set": {"ciphertext": CryptoService.encode_ciphertext(tampered)}},
        )

    @staticmethod
    def _normalize_ipfs_api(addr: str) -> str:
        if addr.startswith("/dns/") and addr.endswith("/http"):
            parts = addr.strip("/").split("/")
            host = parts[1]
            port = parts[3]
            return f"http://{host}:{port}"
        if addr.startswith("http://") or addr.startswith("https://"):
            return addr.rstrip("/")
        return f"http://{addr.strip('/')}"

    def _ipfs_add_bytes(self, payload: bytes) -> str:
        response = requests.post(
            f"{self.ipfs_api}/api/v0/add",
            files={"file": ("payload.json", BytesIO(payload), "application/json")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["Hash"]

    def _ipfs_cat(self, cid: str) -> bytes:
        response = requests.post(
            f"{self.ipfs_api}/api/v0/cat",
            params={"arg": cid},
            timeout=30,
        )
        response.raise_for_status()
        return response.content
