"""Resolve a verified JWT subject to the current role and optional KG account."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from macrostrat_db_insertion.security.model import UserAccess
from macrostrat_db_insertion.security.schema import AuthUser, KGUser


def get_user_access(sub: str, session: Session) -> UserAccess | None:
    """Read only. A lookup by sub alone does not authenticate that person."""
    row = session.execute(
        select(AuthUser.sub, AuthUser.role, KGUser.internal_user_id)
        .select_from(AuthUser)
        .outerjoin(KGUser, KGUser.external_user_id == AuthUser.sub)
        .where(AuthUser.sub == sub)
    ).mappings().one_or_none()

    if row is None:
        return None
    return UserAccess(**row)
