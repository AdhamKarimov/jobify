from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import date

from db import get_db
from applies.models import Apply
from applies.schema import ApplyCreate, ApplyResponse, ApplyStatusUpdate, ApplyStatusEnum
from users.models import User, UserRole
from users.utilis import check_role
from vakansiya.models import Vakansiya

router = APIRouter(prefix="/apply", tags=["apply"])

CANDIDATE_ROLES = [UserRole.USER]
COMPANY_ROLES = [UserRole.COMPANY, UserRole.ADMIN]
ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]


@router.post("/create", response_model=ApplyResponse, status_code=status.HTTP_201_CREATED)
async def apply_vacancy(
    data: ApplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Vakansiya).filter(
            Vakansiya.id == data.vacancy_id,
            Vakansiya.is_deleted == False,
            Vakansiya.is_active == True
        )
    )
    vacancy = result.scalars().first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi yoki faol emas")

    if vacancy.deadline and vacancy.deadline < date.today():
        raise HTTPException(status_code=400, detail="Vakansiya muddati tugagan")

    existing = await db.execute(
        select(Apply).filter(
            Apply.vacancy_id == data.vacancy_id,
            Apply.candidate_id == current_user.id
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Siz bu vakansiyaga allaqachon apply qilgansiz")

    new_apply = Apply(
        vacancy_id=data.vacancy_id,
        candidate_id=current_user.id
    )
    db.add(new_apply)
    await db.commit()
    await db.refresh(new_apply)

    result = await db.execute(
        select(Apply)
        .options(joinedload(Apply.vacancy), joinedload(Apply.candidate))
        .filter(Apply.id == new_apply.id)
    )
    return result.scalars().first()


@router.get("/my", response_model=List[ApplyResponse])
async def my_applies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Apply)
        .options(joinedload(Apply.vacancy), joinedload(Apply.candidate))
        .filter(Apply.candidate_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/vacancy/{vacancy_id}", response_model=List[ApplyResponse])
async def vacancy_applies(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(COMPANY_ROLES))
):
    result = await db.execute(
        select(Vakansiya).filter(
            Vakansiya.id == vacancy_id,
            Vakansiya.is_deleted == False
        )
    )
    vacancy = result.scalars().first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    if vacancy.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")

    result = await db.execute(
        select(Apply)
        .options(joinedload(Apply.vacancy), joinedload(Apply.candidate))
        .filter(Apply.vacancy_id == vacancy_id)
    )
    return result.scalars().all()



@router.patch("/status/{apply_id}", response_model=ApplyResponse)
async def update_apply_status(
    apply_id: int,
    data: ApplyStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(COMPANY_ROLES))
):
    result = await db.execute(
        select(Apply)
        .options(joinedload(Apply.vacancy), joinedload(Apply.candidate))
        .filter(Apply.id == apply_id)
    )
    apply = result.scalars().first()
    if not apply:
        raise HTTPException(status_code=404, detail="Apply topilmadi")

    if apply.vacancy.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")

    apply.status = data.status
    await db.commit()
    await db.refresh(apply)

    result = await db.execute(
        select(Apply)
        .options(joinedload(Apply.vacancy), joinedload(Apply.candidate))
        .filter(Apply.id == apply_id)
    )
    return result.scalars().first()


@router.delete("/delete/{apply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apply(
    apply_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(CANDIDATE_ROLES))
):
    result = await db.execute(
        select(Apply).filter(Apply.id == apply_id)
    )
    apply = result.scalars().first()
    if not apply:
        raise HTTPException(status_code=404, detail="Apply topilmadi")

    if apply.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")

    await db.delete(apply)
    await db.commit()