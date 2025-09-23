from datetime import datetime

from pydantic import BaseModel


class InsightsRequest(BaseModel):
    facility: str
    start_time: datetime
    end_time: datetime
