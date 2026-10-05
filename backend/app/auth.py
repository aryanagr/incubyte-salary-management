from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Literal

from fastapi import Cookie, Depends, HTTPException, status

SESSION_COOKIE = "salary_demo_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
Role = Literal["hr_manager", "hr"]


@dataclass(frozen=True)
class DemoUser:
    email: str
    name: str
    role: Role
    password: str


DEMO_USERS: dict[str, DemoUser] = {
    "manager@salary.demo": DemoUser(
        email="manager@salary.demo",
        name="Maya Sharma",
        role="hr_manager",
        password="Manager@123",
    ),
    "hr@salary.demo": DemoUser(
        email="hr@salary.demo",
        name="Rohan Mehta",
        role="hr",
        password="Hr@123",
    ),
}


def _secret() -> bytes:
    configured = os.getenv("AUTH_SECRET")
    if configured:
        if os.getenv("VERCEL") == "1" and len(configured) < 32:
            raise RuntimeError("AUTH_SECRET must be at least 32 characters in production")
        return configured.encode("utf-8")

    if os.getenv("VERCEL") == "1":
        raise RuntimeError("AUTH_SECRET is required in production")

    # Local development and tests stay self-contained without weakening the
    # deployed environment, which must always provide its own secret.
    return b"local-development-only-secret"


def authenticate(email: str, password: str) -> DemoUser | None:
    user = DEMO_USERS.get(email.strip().lower())
    if not user or not secrets.compare_digest(password, user.password):
        return None
    return user


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_session_token(user: DemoUser) -> str:
    payload = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "exp": int(time.time()) + SESSION_TTL_SECONDS,
    }
    encoded = _b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{_b64encode(signature)}"


def parse_session_token(token: str) -> DemoUser | None:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(signature)):
            return None
        payload = json.loads(_b64decode(encoded))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        email = str(payload.get("email", ""))
        user = DEMO_USERS.get(email)
        if not user:
            return None
        if payload.get("role") != user.role or payload.get("name") != user.name:
            return None
        return user
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def current_user(salary_demo_session: str | None = Cookie(default=None)) -> DemoUser:
    if not salary_demo_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    user = parse_session_token(salary_demo_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    return user


def require_manager(user: DemoUser = Depends(current_user)) -> DemoUser:
    if user.role != "hr_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR Manager permission required")
    return user
