from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mqtt_host: str = os.getenv("MQTT_HOST", "127.0.0.1")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_topic: str = os.getenv("MQTT_TOPIC", "iot/data")

    api_host: str = os.getenv("API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
    mongo_db: str = os.getenv("MONGO_DB", "iot_security")
    mongo_collection: str = os.getenv("MONGO_COLLECTION", "records")

    ipfs_addr: str = os.getenv("IPFS_ADDR", "/dns/127.0.0.1/tcp/5001/http")

    eth_rpc_url: str = os.getenv("ETH_RPC_URL", "http://127.0.0.1:8545")
    eth_chain_id: int = int(os.getenv("ETH_CHAIN_ID", "31337"))
    eth_contract_address: str = os.getenv("ETH_CONTRACT_ADDRESS", "")
    eth_account_address: str = os.getenv("ETH_ACCOUNT_ADDRESS", "")
    eth_private_key: str = os.getenv("ETH_PRIVATE_KEY", "")
    eth_contract_abi: str = os.getenv("ETH_CONTRACT_ABI", "blockchain/abi/AdaptiveSecurityAudit.json")


settings = Settings()
