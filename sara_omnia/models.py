from datetime import datetime

from pydantic import BaseModel


class RequestModel(BaseModel):
    name: str
    facility: str
    externalId: str
    description: str
    unit: str
    assetId: str
    value: float
    timestamp: datetime
    step: bool = True
    metadata: dict = {}
