from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI

from api.db.models import ApplicationInfo, HealthCheck
from api.routers import auth, items, users
from api.utils.config import Settings
from api.utils.dependencies import get_settings

app = FastAPI()

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(users.router)


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]) -> ApplicationInfo:
    return ApplicationInfo(app_name=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/health")
async def health_check() -> HealthCheck:
    return HealthCheck(status="ok", timestamp=datetime.now(UTC))
