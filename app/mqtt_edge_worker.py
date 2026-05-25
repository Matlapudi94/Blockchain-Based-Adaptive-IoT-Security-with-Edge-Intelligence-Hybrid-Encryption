from __future__ import annotations

import json

import paho.mqtt.client as mqtt

from app.config import settings
from app.models import IoTRecord
from app.orchestrator import SystemOrchestrator


class EdgeMQTTWorker:
    def __init__(self) -> None:
        self.orchestrator = SystemOrchestrator()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
        client.subscribe(settings.mqtt_topic)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        payload = json.loads(msg.payload.decode("utf-8"))
        record = IoTRecord(**payload)
        result = self.orchestrator.ingest_record(record)
        print(f"Processed record {result['record']['record_id']} with mode {result['decision']['encryption_mode']}")

    def run(self) -> None:
        self.client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        self.client.loop_forever()
