import re
import os
from redis.asyncio import Redis
from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from users.models import User, UserRole
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_jwt_auth2 import AuthJWT

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
username_regex = re.compile(r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$', re.IGNORECASE)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = Redis.from_url(REDIS_URL)


def check_username_or_email(username_or_email):
    if not isinstance(username_or_email, str) or not username_or_email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email yoki username kiritilmadi"
        )
    username_or_email = username_or_email.strip()
    if re.fullmatch(email_regex, username_or_email):
        return 'email'
    elif re.fullmatch(username_regex, username_or_email):
        return 'username'
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Login yoki parol xato"
    )


def check_role(allowed_roles: list[UserRole]):
    async def role_checker(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):

        Authorize.jwt_required()

        # Blacklist tekshiruvi
        jti = Authorize.get_raw_jwt()["jti"]
        is_blacklisted = await redis_client.get(f"blacklist:{jti}")
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Token yaroqsiz, qayta login qiling")

        current_username = Authorize.get_jwt_subject()
        result = await db.execute(select(User).filter(User.username == current_username))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Sizda ushbu amalni bajarish uchun ruxsat yo'q")

        return user

    return role_checker