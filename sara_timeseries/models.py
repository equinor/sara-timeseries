from datetime import datetime

from omnia_timeseries.models import MessageModel
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


class ResponseModel(BaseModel):
    timeseriesId: str
    details: MessageModel
