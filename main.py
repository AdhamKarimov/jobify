from fastapi import FastAPI
from fastapi_jwt_auth2 import AuthJWT
from users.schema import Settings
from db import Base, engine

from users.router import router as users_router
from vakansiya.router import router as vacancy_router
from applies.router import router as apply_router
from notification.router import router as notification_router
from favorite.router import router as favorite_router

from users.models import User
from vakansiya.models import Vakansiya
from applies.models import Apply
from favorite.models import Favorite
from notification.models import Notification


app = FastAPI(
    title="Jobify API",
    description="Ish topish platformasi — HR va Candidate uchun",
    version="1.0.0",
)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(users_router)
app.include_router(vacancy_router)
app.include_router(apply_router)
app.include_router(notification_router)
app.include_router(favorite_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Jobify API ga xush kelibsiz!",
        "docs": "/docs",
        "redoc": "/redoc"
    }