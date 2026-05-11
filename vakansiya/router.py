from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from vakansiya.models import Vakansiya
from vakansiya.schema import VacancyCreate, VacancyDetail, VacancyListResponse, VacancyUpdate
from users.models import User, UserRole
from users.utilis import check_role
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/vacancy", tags=["vacancy"])

COMPANY_ROLES = [UserRole.COMPANY, UserRole.ADMIN]
ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]


@router.post("/create", response_model=VacancyDetail, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    data: VacancyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(COMPANY_ROLES))
):
    new_vacancy = Vakansiya(
        title=data.title,
        description=data.description,
        salary=data.salary,
        location=data.location,
        deadline=data.deadline,
        author_id=current_user.id
    )
    db.add(new_vacancy)
    await db.commit()
    await db.refresh(new_vacancy)

    result = await db.execute(
        select(Vakansiya)
        .options(joinedload(Vakansiya.author))
        .filter(Vakansiya.id == new_vacancy.id)
    )
    vacancy = result.scalars().first()
    return vacancy


@router.get("/list", response_model=List[VacancyListResponse])
async def vacancy_list(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Title bo'yicha qidirish"),
    location: Optional[str] = Query(None, description="Shahar bo'yicha filter"),
    is_active: Optional[bool] = Query(None, description="Faol vakansiyalar"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = select(Vakansiya).filter(Vakansiya.is_deleted == False)

    if search:
        query = query.filter(Vakansiya.title.ilike(f"%{search}%"))
    if location:
        query = query.filter(Vakansiya.location.ilike(f"%{location}%"))
    if is_active is not None:
        query = query.filter(Vakansiya.is_active == is_active)

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    vacancies = result.scalars().all()
    return vacancies


@router.get("/detail/{vacancy_id}", response_model=VacancyDetail)
async def vacancy_detail(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Vakansiya)
        .options(joinedload(Vakansiya.author))
        .filter(Vakansiya.id == vacancy_id, Vakansiya.is_deleted == False)
    )
    vacancy = result.scalars().first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    vacancy.view_count += 1
    await db.commit()
    await db.refresh(vacancy)

    return vacancy


@router.patch("/update/{vacancy_id}", response_model=VacancyDetail)
async def update_vacancy(
    vacancy_id: int,
    new_data: VacancyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(COMPANY_ROLES))
):
    result = await db.execute(
        select(Vakansiya)
        .options(joinedload(Vakansiya.author))
        .filter(Vakansiya.id == vacancy_id, Vakansiya.is_deleted == False)
    )
    vacancy = result.scalars().first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    if vacancy.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")

    if new_data.title is not None:
        vacancy.title = new_data.title
    if new_data.description is not None:
        vacancy.description = new_data.description
    if new_data.salary is not None:
        vacancy.salary = new_data.salary
    if new_data.location is not None:
        vacancy.location = new_data.location
    if new_data.deadline is not None:
        vacancy.deadline = new_data.deadline
    if new_data.is_active is not None:
        vacancy.is_active = new_data.is_active

    await db.commit()
    await db.refresh(vacancy)
    return vacancy


@router.delete("/delete/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(COMPANY_ROLES))
):
    result = await db.execute(
        select(Vakansiya).filter(Vakansiya.id == vacancy_id, Vakansiya.is_deleted == False)
    )
    vacancy = result.scalars().first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vakansiya topilmadi")

    if vacancy.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sizda ruxsat yo'q")
    vacancy.is_deleted = True
    await db.commit()