"""Shared SaaS security helpers.

Use these dependencies in tenant-owned routes. A user ID supplied in a query
parameter or request body is not an authentication credential.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.auth_routes import get_current_user
from database.models import Brand, User
from database.session import get_db


def require_active_user(user: User = Depends(get_current_user)) -> User:
    """Resolve the authenticated account and reject disabled users."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return user


def get_owned_brand(
    brand_id: int,
    user: User,
    db: Session,
) -> Brand:
    """Return a brand only if it belongs to the authenticated user."""
    brand: Optional[Brand] = (
        db.query(Brand)
        .filter(Brand.id == brand_id, Brand.owner_id == user.id)
        .first()
    )
    if brand is None:
        # Avoid disclosing whether another user's resource exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    return brand


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """Named dependency for clearer endpoint declarations."""
    return db
