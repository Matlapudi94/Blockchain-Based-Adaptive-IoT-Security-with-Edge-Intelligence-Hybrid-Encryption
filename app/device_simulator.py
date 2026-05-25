from __future__ import annotations

from dataclasses import asdict
import json
from threading import Event

import paho.mqtt.client as mqtt

from app.config import settings
from app.models import IoTRecord


class DeviceSimulator:
    def __init__(self) -> None:
        self._connected = Event()

    def generate(self) -> list[IoTRecord]:
        return [
            IoTRecord(
                device_id="ecg-07",
                data_type="heart_rate",
                payload={"bpm": 132, "patient_id": "P-104"},
                context="healthcare",
                real_time=True,
                latency_budget_ms=50,
                sensitivity_hint=92,
            ),
            IoTRecord(
                device_id="meter-19",
                data_type="traffic_summary",
                payload={"junction": "A12", "count": 184},
                context="smart_city",
                real_time=False,
                latency_budget_ms=300,
                sensitivity_hint=58,
            ),
            IoTRecord(
                device_id="weather-03",
                data_type="temperature",
                payload={"celsius": 31.4, "zone": "public-park"},
                context="smart_city",
                real_time=False,
                latency_budget_ms=500,
                sensitivity_hint=18,
            ),
            IoTRecord(
                device_id="press-02",
                data_type="maintenance_stats",
                payload={"rpm": 1200, "operator_id": "EMP-9"},
                context="industrial",
                real_time=False,
                latency_budget_ms=250,
                sensitivity_hint=86,
            ),
        ]

    def publish(self, client: mqtt.Client | None = None) -> None:
        owns_client = client is None
        mqtt_client = client or mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if owns_client:
            mqtt_client.on_connect = self._on_connect
            mqtt_client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
            mqtt_client.loop_start()
            if not self._connected.wait(timeout=5):
                mqtt_client.loop_stop()
                raise RuntimeError("MQTT broker connection timed out.")

        for record in self.generate():
            info = mqtt_client.publish(settings.mqtt_topic, json.dumps(asdict(record), sort_keys=True))
            info.wait_for_publish()

        if owns_client:
            mqtt_client.disconnect()
            mqtt_client.loop_stop()

    def _on_connect(self, client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
        if reason_code == 0:
            self._connected.set()
