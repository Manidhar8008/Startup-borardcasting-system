"""Focused tests for SaaS identity and resource ownership safeguards."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from core.saas_security import get_owned_brand, require_active_user


def test_inactive_user_is_rejected():
    user = SimpleNamespace(is_active=False)
    with pytest.raises(HTTPException) as exc:
        require_active_user(user)
    assert exc.value.status_code == 403


def test_active_user_is_accepted():
    user = SimpleNamespace(is_active=True)
    assert require_active_user(user) is user


def test_owned_brand_is_scoped_to_authenticated_owner():
    class Query:
        def filter(self, *args):
            return self

        def first(self):
            return None

    class DB:
        def query(self, model):
            return Query()

    user = SimpleNamespace(id=20)
    with pytest.raises(HTTPException) as exc:
        get_owned_brand(brand_id=42, user=user, db=DB())
    assert exc.value.status_code == 404
    assert exc.value.detail == "Brand not found"
