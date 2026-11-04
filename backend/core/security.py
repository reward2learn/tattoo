import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Response

JWT_ALGORITHM = "HS256"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=7)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str | None) -> bool:
    return bool(hashed) and bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: str, session_version: int, kind: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "sv": session_version, "type": kind, "iat": now,
               "exp": now + (ACCESS_TTL if kind == "access" else REFRESH_TTL)}
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, os.environ["JWT_SECRET"], algorithms=[JWT_ALGORITHM])


def _cookie(response: Response, key: str, value: str, ttl: timedelta) -> None:
    response.set_cookie(key=key, value=value, httponly=True, secure=True, samesite="none",
                        max_age=int(ttl.total_seconds()), path="/")


def set_auth_cookies(response: Response, user_id: str, session_version: int) -> None:
    _cookie(response, "access_token", create_token(user_id, session_version, "access"), ACCESS_TTL)
    _cookie(response, "refresh_token", create_token(user_id, session_version, "refresh"), REFRESH_TTL)


def set_access_cookie(response: Response, user_id: str, session_version: int) -> None:
    _cookie(response, "access_token", create_token(user_id, session_version, "access"), ACCESS_TTL)


def clear_auth_cookies(response: Response) -> None:
    for key in ("access_token", "refresh_token"):
        response.delete_cookie(key, path="/", secure=True, httponly=True, samesite="none")
