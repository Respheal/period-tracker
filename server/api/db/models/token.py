from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(SQLModel):
    sub: str
    exp: int | float
    roles: list[str] = []


class TokenData(SQLModel):
    username: str | None = None
    roles: list[str] = []
