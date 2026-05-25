from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract

from app.config import settings
from app.models import AuditRecord, Decision, IoTRecord, StoredObject


class SmartContractClient:
    def __init__(self) -> None:
        if not settings.eth_contract_address:
            raise RuntimeError("ETH_CONTRACT_ADDRESS is not configured.")
        if not settings.eth_account_address or not settings.eth_private_key:
            raise RuntimeError("ETH_ACCOUNT_ADDRESS and ETH_PRIVATE_KEY are required for contract writes.")

        self.web3 = Web3(Web3.HTTPProvider(settings.eth_rpc_url))
        abi_path = Path(settings.eth_contract_abi)
        abi = json.loads(abi_path.read_text(encoding="utf-8"))
        self.contract: Contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(settings.eth_contract_address),
            abi=abi,
        )
        self.account: LocalAccount = self.web3.eth.account.from_key(settings.eth_private_key)
        self.account_address = Web3.to_checksum_address(settings.eth_account_address)

    def _send(self, fn: Any) -> Any:
        nonce = self.web3.eth.get_transaction_count(self.account_address)
        tx = fn.build_transaction(
            {
                "from": self.account_address,
                "nonce": nonce,
                "chainId": settings.eth_chain_id,
                "gas": 1_200_000,
                "gasPrice": self.web3.to_wei("2", "gwei"),
            }
        )
        signed = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    @staticmethod
    def _key(value: str) -> bytes:
        return Web3.keccak(text=value)

    def validate_decision(self, classification: str, decision: str) -> bool:
        return self.contract.functions.validateDecision(classification, decision).call()

    def log_decision(self, record: IoTRecord, decision: Decision, stored: StoredObject) -> None:
        self._send(
            self.contract.functions.logDecision(
                self._key(record.record_id),
                record.record_id,
                record.device_id,
                decision.classification,
                decision.encryption_mode,
                stored.storage_ref,
                stored.storage_kind,
                record.timestamp,
            )
        )

    def log_hash(self, data_id: str, hash_value: str) -> None:
        self._send(self.contract.functions.logHash(self._key(data_id), hash_value))

    def authorize(self, user_wallet: str, device_id: str) -> bool:
        return self.contract.functions.authorizeAccess(
            Web3.to_checksum_address(user_wallet),
            self._key(device_id),
        ).call()

    def grant_access(self, user_wallet: str, device_id: str) -> None:
        self._send(
            self.contract.functions.grantAccess(
                Web3.to_checksum_address(user_wallet),
                self._key(device_id),
            )
        )

    def get_hash(self, data_id: str) -> str:
        return self.contract.functions.getHash(self._key(data_id)).call()

    def get_audit_record(self, data_id: str) -> AuditRecord:
        result = self.contract.functions.getDecision(self._key(data_id)).call()
        return AuditRecord(
            data_id=result[0],
            device_id=result[1],
            classification=result[2],
            decision=result[3],
            storage_ref=result[4],
            storage_kind=result[5],
            timestamp=result[6],
            hash_value=self.get_hash(data_id),
        )
