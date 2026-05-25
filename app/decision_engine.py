from __future__ import annotations

from app.models import Decision, EdgeMetrics


class DecisionEngine:
    def decide(self, metrics: EdgeMetrics) -> Decision:
        sensitivity = metrics.sensitivity_score
        if sensitivity >= 80:
            if metrics.real_time or metrics.latency_budget_ms <= 100:
                return Decision(
                    classification="HIGH",
                    encryption_mode="AES_FULL",
                    reason="High sensitivity with real-time or tight latency",
                )
            return Decision(
                classification="HIGH",
                encryption_mode="AES_PHE",
                reason="High sensitivity without real-time pressure",
            )
        if sensitivity >= 40:
            return Decision(
                classification="MEDIUM",
                encryption_mode="AES_MASK",
                reason="Medium sensitivity balanced with utility retention",
            )
        if metrics.resource_score < 40 or metrics.latency_budget_ms <= 150:
            return Decision(
                classification="LOW",
                encryption_mode="LIGHTWEIGHT",
                reason="Low sensitivity under resource or latency constraints",
            )
        return Decision(
            classification="LOW",
            encryption_mode="NONE",
            reason="Low sensitivity and relaxed conditions",
        )
