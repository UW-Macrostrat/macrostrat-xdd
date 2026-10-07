"""Verified identity and database-backed feedback permissions."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TokenData(BaseModel):
    sub: str


class UserAccess(BaseModel):
    model_config = ConfigDict(frozen=True)

    sub: str
    role: str
    internal_user_id: UUID | None = None

    @property
    def has_kg_account(self) -> bool:
        return self.internal_user_id is not None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def can_submit_feedback(self) -> bool:
        return self.role in {"user", "admin"}

    def can_manage_feedback(self, owner_user_id: UUID | str | None) -> bool:
        """Call only for a feedback run; owner_user_id is all_runs.user_id."""
        if owner_user_id is None:
            return False
        return self.is_admin or (
            self.role == "user"
            and self.internal_user_id is not None
            and str(self.internal_user_id) == str(owner_user_id)
        )
