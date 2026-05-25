# Blockchain-Centric Adaptive IoT Security Stack

This project now implements the architecture as a real local stack instead of an in-memory prototype.

## Real Components

- MQTT broker for IoT data transport
- FastAPI REST API for ingestion and retrieval
- MongoDB for database-backed encrypted storage
- IPFS node for decentralized object storage
- Ethereum-compatible blockchain with Solidity smart contracts
- True Paillier-based partial homomorphic encryption for the `AES + PHE` branch

## Architecture Mapping

1. IoT device publishes data to MQTT
2. Edge worker subscribes and performs edge analysis
3. Decision engine selects `AES_FULL`, `AES_PHE`, `AES_MASK`, `LIGHTWEIGHT`, or `NONE`
4. Smart contract validates the decision
5. Encrypted data is stored in MongoDB or IPFS
6. SHA-256 hash is generated
7. Hash and metadata are logged on blockchain
8. REST API handles user retrieval
9. Smart contract enforces access control
10. Hash is verified before decryption

## Local Services You Need Running

- MQTT broker, default `localhost:1883`
- MongoDB, default `mongodb://localhost:27017`
- IPFS API, default `/dns/127.0.0.1/tcp/5001/http`
- Hardhat local node or another Ethereum RPC, default `http://127.0.0.1:8545`

## Python Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Node / Hardhat Setup

```powershell
cd blockchain
npm.cmd install
npm.cmd run node
```

In another terminal:

```powershell
cd blockchain
npm.cmd run deploy
```

## Python Commands

Start the API:

```powershell
python main.py serve-api
```

Start the MQTT edge worker:

```powershell
python main.py run-edge
```

Publish demo IoT records:

```powershell
python main.py publish-demo
```

Grant blockchain access for a wallet to a device:

```powershell
python main.py grant-access --wallet 0xYourWallet --device ecg-07
```

## Environment

Copy `.env.example` to `.env` and update values if needed.
