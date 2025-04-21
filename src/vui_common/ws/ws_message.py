from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class WebSocketMessage(BaseModel):
    type: str
    kind: Literal["request", "response", "event", "error", "command"]
    payload: Optional[dict] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None

def build_message(type_: str, kind: str, payload: dict = None, request_id: Optional[str] = None):
    return {
        "type": type_,
        "kind": kind,
        "payload": payload or {},
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
