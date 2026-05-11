from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Text,Boolean,UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Apply(Base):
    __tablename__ = "applies"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending")
    applied_at = Column(DateTime, default=datetime.utcnow)


    vacancy = relationship("Vakansiya", back_populates="applies")
    candidate = relationship("User", back_populates="applies")
    __table_args__ = (UniqueConstraint('vacancy_id', 'candidate_id', name='unique_vacancy_candidate_apply'),)
