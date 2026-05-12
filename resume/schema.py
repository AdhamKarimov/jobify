from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResumeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = 0


class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    is_active: Optional[bool] = None


class ResumeOwnerInfo(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience_years: int
    pdf_file: Optional[str] = None
    is_active: bool
    created_at: datetime
    user: Optional[ResumeOwnerInfo] = None

    class Config:
        from_attributes = True