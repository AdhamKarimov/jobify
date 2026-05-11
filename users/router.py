from users.models import User,UserRole
from users.schema import SignUp, Login, Updateprofil, PasswordResert
from fastapi import APIRouter, HTTPException, Depends, status
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth2 import AuthJWT
import datetime
from redis.asyncio import Redis
from users.utilis import check_role

router = APIRouter(prefix="/users", tags=["users"])
redis = Redis(host="localhost", port=6379)

ALL_ROLES = [UserRole.USER, UserRole.COMPANY, UserRole.ADMIN]
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user: SignUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu Username band")

    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu Email band")

    target_role = user.role
    if target_role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz ADMIN roli bilan ro'yxatdan o'ta olmaysiz!"
        )

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        'status': status.HTTP_201_CREATED,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'username': new_user.username,
        'email': new_user.email,
    }


@router.post("/login")
async def login(data: Login, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    result = await db.execute(select(User).filter(User.username == data.username))
    db_user = result.scalars().first()

    if not db_user or not check_password_hash(db_user.password, data.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username yoki password xato")

    access_token = Authorize.create_access_token(
        subject=db_user.username,
        expires_time=datetime.timedelta(minutes=30)
    )
    refresh_token = Authorize.create_refresh_token(
        subject=db_user.username,
        expires_time=datetime.timedelta(days=7)
    )

    return {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }


@router.get("/profile")
async def profile(
    current_user: User = Depends(check_role(ALL_ROLES))):

    return {
        'status': status.HTTP_200_OK,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    }


@router.put("/update")
async def update_profile(user_data: Updateprofil,db: AsyncSession = Depends(get_db),current_user: User = Depends(check_role(ALL_ROLES))):
    if user_data.first_name:
        current_user.first_name = user_data.first_name
    if user_data.last_name:
        current_user.last_name = user_data.last_name

    if user_data.username and user_data.username != current_user.username:
        res = await db.execute(select(User).filter(User.username == user_data.username))
        if res.scalars().first():
            raise HTTPException(status_code=400, detail="Bu username band")
        current_user.username = user_data.username

    if user_data.email and user_data.email != current_user.email:
        res = await db.execute(select(User).filter(User.email == user_data.email))
        if res.scalars().first():
            raise HTTPException(status_code=400, detail="Bu email band")
        current_user.email = user_data.email

    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ma'lumotlarni saqlashda xatolik yuz berdi")

    return {
        'status': status.HTTP_200_OK,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    }


@router.put("/password-reset")
async def password_reset(data: PasswordResert,db: AsyncSession = Depends(get_db),current_user: User = Depends(check_role(ALL_ROLES))):
    if not check_password_hash(current_user.password, data.old_password):
        raise HTTPException(status_code=400, detail="Eski password xato")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Parollar mos kelmadi")

    current_user.password = generate_password_hash(data.new_password)
    await db.commit()
    return {"detail": "Password yangilandi"}



@router.post("/logout")
async def logout(
    Authorize: AuthJWT = Depends(),
    _ = Depends(check_role(ALL_ROLES))):
    jti = (await Authorize.get_raw_jwt())["jti"]
    await redis.setex(f"blacklist:{jti}", 1800, "true")
    return {"detail": "Muvaffaqiyatli chiqildi"}