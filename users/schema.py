from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from users.models import UserRole

class SignUp(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    email: str
    password: str
    role: UserRole = Field(default=UserRole.USER)

    class Config:
        use_enum_values = True


class Login(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str="9db9dd2b4e07c24272d2d4f84ca8238d1949b53e191786483f4c806d3b13d4c6"



class Updateprofil(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class PasswordResert(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True



class CandidateProfileBase(BaseModel):
    skills: Optional[str] = None
    experience_years: Optional[int] = 0

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileResponse(CandidateProfileBase):
    id: int
    user_id: int
    resume_pdf: Optional[str] = None

    class Config:
        from_attributes = True



class CompanyProfileBase(BaseModel):
    company_name: str
    description: Optional[str] = None
    website: Optional[HttpUrl] = None

class CompanyProfileCreate(CompanyProfileBase):
    pass

class CompanyProfileResponse(CompanyProfileBase):
    id: int
    user_id: int
    logo: Optional[str] = None

    class Config:
        from_attributes = True