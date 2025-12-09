from fastapi import FastAPI

from .routers import items, users

app = FastAPI()


app.include_router(users.router)
app.include_router(items.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Health Check"}
