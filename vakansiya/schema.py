from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class VacancyCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    salary: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[date] = None


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[date] = None
    is_active: Optional[bool] = None


class VacancyAuthorInfo(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class VacancyDetail(BaseModel):
    id: int
    title: str
    description: str
    salary: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[date] = None
    view_count: int
    is_active: bool
    created_at: datetime
    author: VacancyAuthorInfo

    class Config:
        from_attributes = True


class VacancyListResponse(BaseModel):
    id: int
    title: str
    salary: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[date] = None
    view_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True