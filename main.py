from __future__ import annotations

import argparse

import uvicorn

from app.api import create_app
from app.config import settings
from app.device_simulator import DeviceSimulator
from app.mqtt_edge_worker import EdgeMQTTWorker
from app.orchestrator import SystemOrchestrator


def serve_api() -> None:
    uvicorn.run(create_app(), host=settings.api_host, port=settings.api_port)


def publish_demo() -> None:
    simulator = DeviceSimulator()
    simulator.publish()
    print(f"Published demo records to MQTT topic {settings.mqtt_topic}")


def run_edge() -> None:
    EdgeMQTTWorker().run()


def grant_access(wallet: str, device: str) -> None:
    orchestrator = SystemOrchestrator()
    orchestrator.contract.grant_access(wallet, device)
    print(f"Granted {wallet} access to {device}")


def tamper_record(data_id: str) -> None:
    orchestrator = SystemOrchestrator()
    result = orchestrator.tamper_record(data_id)
    print(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Blockchain-centric adaptive IoT security stack")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("serve-api")
    subparsers.add_parser("publish-demo")
    subparsers.add_parser("run-edge")

    grant_parser = subparsers.add_parser("grant-access")
    grant_parser.add_argument("--wallet", required=True)
    grant_parser.add_argument("--device", required=True)

    tamper_parser = subparsers.add_parser("tamper-record")
    tamper_parser.add_argument("--data-id", required=True)

    args = parser.parse_args()
    if args.command == "serve-api":
        serve_api()
    elif args.command == "publish-demo":
        publish_demo()
    elif args.command == "run-edge":
        run_edge()
    elif args.command == "grant-access":
        grant_access(args.wallet, args.device)
    elif args.command == "tamper-record":
        tamper_record(args.data_id)


if __name__ == "__main__":
    main()
