from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.blockchain import SmartContractClient
from app.crypto_service import CryptoService
from app.decision_engine import DecisionEngine
from app.edge_analysis import EdgeAnalysisService
from app.integrity import IntegrityService
from app.models import IoTRecord
from app.storage_service import StorageService


class SystemOrchestrator:
    def __init__(self) -> None:
        self.analysis = EdgeAnalysisService()
        self.decision_engine = DecisionEngine()
        self.crypto = CryptoService()
        self.storage = StorageService()
        self.integrity = IntegrityService()
        self.contract = SmartContractClient()

    def ingest_record(self, record: IoTRecord) -> dict[str, Any]:
        metrics = self.analysis.analyze(record)
        decision = self.decision_engine.decide(metrics)
        if not self.contract.validate_decision(decision.classification, decision.encryption_mode):
            raise ValueError(
                f"Smart contract rejected {decision.encryption_mode} for class {decision.classification}"
            )

        ciphertext, crypto_meta = self.crypto.encrypt(record.payload, decision.encryption_mode)
        storage_kind = "IPFS" if record.data_type in {"maintenance_stats", "image", "video"} else "DATABASE"
        metadata = {
            "record_id": record.record_id,
            "device_id": record.device_id,
            "timestamp": record.timestamp,
            "classification": decision.classification,
            "encryption_mode": decision.encryption_mode,
            "reason": decision.reason,
            "crypto": crypto_meta,
        }
        stored = self.storage.store(record.record_id, ciphertext, metadata, storage_kind)
        hash_value = self.integrity.generate_hash(stored)
        self.contract.log_decision(record, decision, stored)
        self.contract.log_hash(record.record_id, hash_value)
        return {
            "record": asdict(record),
            "metrics": asdict(metrics),
            "decision": asdict(decision),
            "storage_kind": storage_kind,
            "storage_ref": stored.storage_ref,
            "hash": hash_value,
        }

    def retrieve(self, data_id: str, user_wallet: str) -> dict[str, Any]:
        audit = self.contract.get_audit_record(data_id)
        if not self.contract.authorize(user_wallet, audit.device_id):
            return {"status": "ACCESS_DENIED", "data_id": data_id, "wallet": user_wallet}

        stored = self.storage.retrieve(audit.storage_ref, audit.storage_kind)
        current_hash = self.integrity.generate_hash(stored)
        if current_hash != audit.hash_value:
            return {
                "status": "TAMPERING_ALERT",
                "data_id": data_id,
                "expected_hash": audit.hash_value,
                "actual_hash": current_hash,
            }

        plaintext = self.crypto.decrypt(stored.ciphertext, audit.decision)
        return {
            "status": "OK",
            "data_id": data_id,
            "device_id": audit.device_id,
            "classification": audit.classification,
            "encryption_mode": audit.decision,
            "payload": plaintext,
        }

    def tamper_record(self, data_id: str) -> dict[str, str]:
        audit = self.contract.get_audit_record(data_id)
        self.storage.tamper(audit.storage_ref, audit.storage_kind)
        return {
            "status": "TAMPERED",
            "data_id": data_id,
            "storage_kind": audit.storage_kind,
            "storage_ref": audit.storage_ref,
        }
