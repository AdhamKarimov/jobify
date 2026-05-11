from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_db
from notification.models import Notification
from notification.schema import NotificationResponse, NotificationMarkRead
from users.models import User, UserRole
from users.utilis import check_role

router = APIRouter(prefix="/notifications", tags=["notifications"])

ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]


@router.get("/my_notification", response_model=List[NotificationResponse])
async def my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    count = len(result.scalars().all())
    return {"unread_count": count}


@router.patch("/read/{notification_id}", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification topilmadi")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


@router.patch("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    notifications = result.scalars().all()
    for notification in notifications:
        notification.is_read = True

    await db.commit()
    return {"detail": f"{len(notifications)} ta notification o'qildi"}


@router.delete("/delete/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_role(ALL_ROLES))
):
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification topilmadi")

    await db.delete(notification)
    await db.commit()