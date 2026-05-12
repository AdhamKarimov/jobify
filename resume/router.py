import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from db import get_db
from resume.models import Resume
from resume.schema import ResumeCreate, ResumeUpdate, ResumeResponse
from users.models import User, UserRole
from users.utilis import check_role

router = APIRouter(prefix="/resume", tags=["resume"])

UPLOAD_DIR = "media/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024
CANDIDATE_ROLES = [UserRole.USER]
ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]


@router.post("/create", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    data: ResumeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    new_resume = Resume(
        user_id=current_user.id,
        title=data.title,
        summary=data.summary,
        skills=data.skills,
        experience_years=data.experience_years
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)

    result = await db.execute(
        select(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == new_resume.id)
    )
    return result.scalars().first()


@router.post("/upload-pdf/{resume_id}", response_model=ResumeResponse)
async def upload_pdf(
    resume_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Faqat PDF fayl yuklanadi")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fayl hajmi 5MB dan oshmasligi kerak")

    result = await db.execute(
        select(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")

    if resume.pdf_file and os.path.exists(resume.pdf_file):
        os.remove(resume.pdf_file)

    filename = f"{uuid.uuid4()}.pdf"
    file_path = f"{UPLOAD_DIR}/{filename}"
    with open(file_path, "wb") as f:
        f.write(contents)

    resume.pdf_file = file_path
    await db.commit()
    await db.refresh(resume)

    result = await db.execute(
        select(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == resume_id)
    )
    return result.scalars().first()


@router.get("/my", response_model=List[ResumeResponse])
async def my_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
    )
    return result.scalars().all()


@router.get("/detail/{resume_id}", response_model=ResumeResponse)
async def resume_detail(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == resume_id)
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")

    if (resume.user_id != current_user.id and
        current_user.role not in [UserRole.COMPANY, UserRole.ADMIN]):
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")

    return resume

@router.patch("/update", response_model=ResumeResponse)
async def update_resume(
    data: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Resume).filter(
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")

    if data.title is not None:
        resume.title = data.title
    if data.summary is not None:
        resume.summary = data.summary
    if data.skills is not None:
        resume.skills = data.skills
    if data.experience_years is not None:
        resume.experience_years = data.experience_years
    if data.is_active is not None:
        resume.is_active = data.is_active

    await db.commit()
    await db.refresh(resume)

    result = await db.execute(
        select(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == resume.id)
    )
    return result.scalars().first()


@router.delete("/delete/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume topilmadi")

    if resume.pdf_file and os.path.exists(resume.pdf_file):
        os.remove(resume.pdf_file)
        raise HTTPException(status_code=204, detail="Resume o'chirildi")

    await db.delete(resume)
    await db.commit()