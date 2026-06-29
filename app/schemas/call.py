from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CallBase(BaseModel):
    room_id: str
    caller_id: str


class CallCreate(CallBase):
    pass


class Call(CallBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(..., alias="_id")
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in seconds
    status: str  # e.g., 'ongoing', 'completed', 'rejected', 'missed'
