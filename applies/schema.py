from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
from enum import Enum


class ApplyStatusEnum(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class VacancyShortInfo(BaseModel):
    id: int
    title: str
    location: Optional[str] = None

    class Config:
        from_attributes = True


class CandidateShortInfo(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class ApplyCreate(BaseModel):
    vacancy_id: int


class ApplyStatusUpdate(BaseModel):
    status: ApplyStatusEnum

    class Config:
        use_enum_values = True


class ApplyResponse(BaseModel):
    id: int
    vacancy_id: int
    candidate_id: int
    status: ApplyStatusEnum
    applied_at: datetime
    vacancy: Optional[VacancyShortInfo] = None
    candidate: Optional[CandidateShortInfo] = None

    class Config:
        from_attributes = True