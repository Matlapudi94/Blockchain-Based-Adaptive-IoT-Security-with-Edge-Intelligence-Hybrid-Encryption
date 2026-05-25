from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.models import IoTRecord
from app.orchestrator import SystemOrchestrator


class IngestRequest(BaseModel):
    device_id: str
    data_type: str
    payload: dict
    context: str
    real_time: bool
    latency_budget_ms: int = Field(ge=1)
    sensitivity_hint: int = Field(ge=0, le=100)


class RetrievalRequest(BaseModel):
    user_wallet: str


def create_app() -> FastAPI:
    app = FastAPI(title="Blockchain-Centric Adaptive IoT Security API")
    orchestrator = SystemOrchestrator()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/ingest")
    def ingest(payload: IngestRequest) -> dict:
        record = IoTRecord(**payload.model_dump())
        try:
            return orchestrator.ingest_record(record)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/records/{data_id}/retrieve")
    def retrieve(data_id: str, request: RetrievalRequest) -> dict:
        try:
            return orchestrator.retrieve(data_id, request.user_wallet)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/records/{data_id}/tamper")
    def tamper(data_id: str) -> dict:
        try:
            return orchestrator.tamper_record(data_id)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app
