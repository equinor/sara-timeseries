from datetime import datetime
from typing import Dict, List

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
    statusCode: int
    message: str


class DatapointsRequestModel(BaseModel):
    facility: str
    start_time: datetime
    end_time: datetime


class CO2ConcentrationRequestModel(BaseModel):
    facility: str
    task_start_time: datetime
    task_end_time: datetime
    inspection_name: str


class DatapointsResponseModel(BaseModel):
    data: List[Dict]
