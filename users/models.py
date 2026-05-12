from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum,ForeignKey,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base
import enum


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    resume_pdf = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)

    user = relationship("User", back_populates="candidate_profile")


class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    company_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo = Column(String, nullable=True)

    user = relationship("User", back_populates="company_profile")



class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    COMPANY  = "company"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    vacancy = relationship("Vakansiya", back_populates="author", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete")
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False, cascade="all, delete")
    applies = relationship("Apply", back_populates="candidate", cascade="all, delete")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return self.username