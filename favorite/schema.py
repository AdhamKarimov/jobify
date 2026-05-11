from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VacancyShortInfo(BaseModel):
    id: int
    title: str
    salary: Optional[str] = None
    location: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    created_at: datetime
    vacancy: Optional[VacancyShortInfo] = None

    class Config:
        from_attributes = True