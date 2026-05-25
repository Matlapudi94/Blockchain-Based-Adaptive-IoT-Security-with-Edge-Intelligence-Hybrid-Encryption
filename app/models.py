from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IoTRecord:
    device_id: str
    data_type: str
    payload: dict[str, Any]
    context: str
    real_time: bool
    latency_budget_ms: int
    sensitivity_hint: int
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=utc_now_iso)


@dataclass
class EdgeMetrics:
    sensitivity_score: int
    resource_score: int
    latency_budget_ms: int
    real_time: bool


@dataclass
class Decision:
    classification: str
    encryption_mode: str
    reason: str


@dataclass
class StoredObject:
    data_id: str
    storage_ref: str
    storage_kind: str
    ciphertext: bytes
    metadata: dict[str, Any]


@dataclass
class AuditRecord:
    data_id: str
    device_id: str
    classification: str
    decision: str
    storage_ref: str
    storage_kind: str
    timestamp: str
    hash_value: str | None = None
