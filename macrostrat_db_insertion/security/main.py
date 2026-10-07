"""Authenticate with the access cookie; authorize using current database roles."""

import logging
import os

from fastapi import Depends, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from macrostrat_db_insertion.database import get_session
from macrostrat_db_insertion.security.db import get_user_access
from macrostrat_db_insertion.security.model import TokenData, UserAccess

logger = logging.getLogger(__name__)


def get_cookie_token(request: Request) -> str | None:
    # Starlette handles the quotes in access_token="Bearer <JWT>".
    scheme, token = get_authorization_scheme_param(
        request.cookies.get("access_token")
    )
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_user_token_from_cookie(
    token: str | None = Depends(get_cookie_token),
) -> TokenData | None:
    if token is None:
        return None

    secret = os.environ.get("SECRET_KEY")
    algorithm = os.environ.get("JWT_ENCRYPTION_ALGORITHM")
    if not secret or not algorithm or algorithm.lower() == "none":
        logger.error("JWT verification is not configured")
        raise HTTPException(503, "Authentication service is not configured")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            options={"require_exp": True, "require_sub": True},
        )
    except (JWTError, ValueError, TypeError):
        return None

    # Central access tokens carry a PostgREST role and no token-type claim.
    # In particular, a refresh JWT must not be accepted as an access JWT.
    if "type" in payload or payload.get("role") not in ("web_user", "web_admin"):
        return None
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        return None
    # The JWT role does NOT grant permissions here; the database role does.
    return TokenData(sub=sub)


def get_user_id(
    token: TokenData | None = Depends(get_user_token_from_cookie),
) -> str | None:
    """Optional verified identity, retained for /health."""
    return token.sub if token is not None else None


def require_feedback_user(
    token: TokenData | None = Depends(get_user_token_from_cookie),
    session: Session = Depends(get_session),
) -> UserAccess:
    if token is None:
        raise HTTPException(401, "Authentication required")

    user = get_user_access(token.sub, session)
    if user is None:
        raise HTTPException(403, "No Macrostrat user account exists for this identity")
    if not user.can_submit_feedback:
        raise HTTPException(403, "User does not have access")
    return user


def require_admin(user: UserAccess) -> None:
    """Explicit guard for model writes on the shared /record_run endpoint."""
    if not user.is_admin:
        raise HTTPException(403, "Administrator access required for model runs")
