from sqlalchemy.ext.asyncio import AsyncSession
from notification.models import Notification


async def create_notification(db: AsyncSession, user_id: int, message: str):
    notification = Notification(
        user_id=user_id,
        message=message
    )
    db.add(notification)
    await db.commit()