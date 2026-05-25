from __future__ import annotations

from app.models import EdgeMetrics, IoTRecord


class EdgeAnalysisService:
    def analyze(self, record: IoTRecord) -> EdgeMetrics:
        resource_score = self._resource_score(record)
        return EdgeMetrics(
            sensitivity_score=max(0, min(100, record.sensitivity_hint)),
            resource_score=resource_score,
            latency_budget_ms=record.latency_budget_ms,
            real_time=record.real_time,
        )

    def _resource_score(self, record: IoTRecord) -> int:
        base = {
            "healthcare": 72,
            "smart_city": 48,
            "industrial": 63,
        }.get(record.context, 50)
        if record.real_time:
            base -= 8
        return max(0, min(100, base))
