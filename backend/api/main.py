from typing import Annotated

from fastapi import Depends, FastAPI

from api.routers import auth, items, users
from api.utils.config import Settings
from api.utils.dependencies import get_settings

app = FastAPI()

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(users.router)


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {"message": settings.APP_NAME}
