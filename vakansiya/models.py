from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime


class Vakansiya(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    deadline = Column(Date, nullable=True)
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="vacancy")
    applies = relationship("Apply", back_populates="vacancy", cascade="all, delete")
    favorites = relationship("Favorite", back_populates="vacancy", cascade="all, delete")