"""Read mappings for existing tables. These do not create or migrate tables."""

from uuid import UUID

from sqlalchemy import Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuthUser(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "macrostrat_auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(Text, unique=True)
    role: Mapped[str] = mapped_column(Text)


class KGUser(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "macrostrat_kg"}

    internal_user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    external_user_id: Mapped[str] = mapped_column(Text, unique=True)
