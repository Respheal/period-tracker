from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.models import ApplicationInfo, HealthCheck
from api.routers import auth, period, symptoms, temperature, users
from api.utils.config import Settings
from api.utils.dependencies import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(period.router)
app.include_router(temperature.router)
app.include_router(symptoms.router)


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]) -> ApplicationInfo:
    return ApplicationInfo(app_name=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/health")
async def health_check() -> HealthCheck:
    return HealthCheck(status="ok", timestamp=datetime.now(UTC))
