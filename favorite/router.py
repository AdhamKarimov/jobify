from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from db import get_db
from favorite.models import Favorite
from favorite.schema import FavoriteResponse
from vakansiya.models import Vakansiya
from users.models import User, UserRole
from users.utilis import check_role

router = APIRouter(prefix="/favorites", tags=["favorites"])

ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]


@router.post("/add/{vacancy_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
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

    result = await db.execute(
        select(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.vacancy_id == vacancy_id
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Bu vakansiya allaqachon favoriteda bor")

    new_favorite = Favorite(
        user_id=current_user.id,
        vacancy_id=vacancy_id
    )
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    result = await db.execute(
        select(Favorite)
        .options(joinedload(Favorite.vacancy))
        .filter(Favorite.id == new_favorite.id)
    )
    return result.scalars().first()


@router.get("/my", response_model=List[FavoriteResponse])
async def my_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Favorite)
        .options(joinedload(Favorite.vacancy))
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/remove/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.vacancy_id == vacancy_id
        )
    )
    favorite = result.scalars().first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite topilmadi")

    await db.delete(favorite)
    await db.commit()


@router.get("/check/{vacancy_id}")
async def check_favorite(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.vacancy_id == vacancy_id
        )
    )
    exists = result.scalars().first() is not None
    return {"is_favorited": exists}