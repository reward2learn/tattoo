from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field

from core.validators import Email

from core.policy import CurrentUser
from core.security import clear_auth_cookies, decode_token, set_access_cookie, set_auth_cookies
from services import auth
from services.users import get_user, user_view

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: Email
    password: str = Field(max_length=128)
    account_type: str = Field(examples=["client", "artist", "studio_owner"])


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(max_length=128)


class GoogleSessionRequest(BaseModel):
    session_id: str = Field(min_length=1)


class AccountTypeRequest(BaseModel):
    account_type: str


async def _signed_in(response: Response, user) -> dict:
    set_auth_cookies(response, user.id, user.session_version)
    return await user_view(user)


@router.post("/register")
async def register(req: RegisterRequest, response: Response):
    user = await auth.register(req.name, req.email, req.password, req.account_type)
    return await _signed_in(response, user)


@router.post("/login")
async def login(req: LoginRequest, request: Request, response: Response):
    ip = (request.headers.get("x-forwarded-for") or request.client.host or "").split(",")[0].strip()
    user = await auth.login(req.email, req.password, ip)
    return await _signed_in(response, user)


@router.post("/google/session")
async def google_session(req: GoogleSessionRequest, response: Response):
    user = await auth.google_exchange(req.session_id)
    return await _signed_in(response, user)


@router.post("/account-type")
async def choose_account_type(req: AccountTypeRequest, user: CurrentUser):
    return await user_view(await auth.set_account_type(user, req.account_type))


@router.get("/me")
async def me(user: CurrentUser):
    return await user_view(user)


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    from fastapi import HTTPException
    token = request.cookies.get("refresh_token")
    try:
        payload = decode_token(token or "")
    except Exception:
        raise HTTPException(401, "Invalid refresh token")
    user = await get_user(payload.get("sub", "")) if payload.get("type") == "refresh" else None
    if not user or user.session_version != payload.get("sv"):
        raise HTTPException(401, "Invalid refresh token")
    set_access_cookie(response, user.id, user.session_version)
    return {"refreshed": True}


@router.post("/logout")
async def logout(request: Request, response: Response):
    from core.policy import get_current_user
    try:
        await auth.end_sessions(await get_current_user(request))
    except Exception:
        pass  # signing out with an already-invalid token still clears cookies
    clear_auth_cookies(response)
    return {"signed_out": True}
