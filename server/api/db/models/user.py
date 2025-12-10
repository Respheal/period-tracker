from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    name: str
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    password: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    roles: list["UserRoles"] = Relationship(back_populates="user", cascade_delete=True)


class UserRoles(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    user: User = Relationship(back_populates="roles")
    role: str
