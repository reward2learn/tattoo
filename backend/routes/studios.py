import re

from fastapi import APIRouter, Depends, File, Request, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.validators import Email

from core.http import public_base_url
from core.policy import CurrentUser, StudioMember, StudioOwner, require_account_type
from services import audit, studios, team
from services.users import User

router = APIRouter(prefix="/api", tags=["studios"])
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
IG_RE = re.compile(r"^@?[A-Za-z0-9._]{1,30}$")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateStudioRequest(Strict):
    name: str = Field(min_length=2, max_length=80)
    slug: str


class BrandingRequest(Strict):
    name: str | None = Field(None, min_length=2, max_length=80)
    primary_color: str | None = None
    accent_color: str | None = None
    tagline: str | None = Field(None, max_length=140)
    about: str | None = Field(None, max_length=2000)
    city: str | None = Field(None, max_length=80)
    contact_email: Email | None = None
    instagram: str | None = None

    @field_validator("primary_color", "accent_color")
    @classmethod
    def hex_color(cls, v):
        if v is not None and not HEX_RE.match(v):
            raise ValueError("Enter a valid hex color like #1A1A1A")
        return v.upper() if v else v

    @field_validator("instagram")
    @classmethod
    def instagram_handle(cls, v):
        if v and not IG_RE.match(v):
            raise ValueError("Enter an Instagram handle like @yourstudio")
        return ("@" + v.lstrip("@")) if v else v


class InviteRequest(Strict):
    email: Email


@router.get("/studios/slug-check")
async def slug_check(slug: str, _: CurrentUser):
    problem = await studios.slug_status(slug)
    return {"slug": slug, "available": problem is None, "message": problem}


@router.post("/studios")
async def create_studio(req: CreateStudioRequest, user: User = Depends(require_account_type("studio_owner"))):
    return studios.studio_view(await studios.create_studio(user.id, req.name.strip(), req.slug))


@router.get("/studios/{slug}/workspace")
async def workspace(ctx: StudioMember):
    return {"studio": studios.studio_view(ctx.studio), "role": ctx.role, "membership_id": ctx.membership_id}


@router.get("/studios/{slug}/settings")
async def get_settings(ctx: StudioOwner):
    return studios.studio_view(ctx.studio)


@router.patch("/studios/{slug}/branding")
async def update_branding(req: BrandingRequest, ctx: StudioOwner):
    changes = req.model_dump(exclude_unset=True)
    changes = {k: ("" if v is None else v) for k, v in changes.items() if k != "name" or v}
    return studios.studio_view(await studios.update_branding(ctx.studio, ctx.user.id, changes))


@router.post("/studios/{slug}/logo")
async def upload_logo(ctx: StudioOwner, file: UploadFile = File(...)):
    data = await file.read(studios.LOGO_MAX_BYTES + 1)
    updated = await studios.save_logo(ctx.studio, ctx.user.id, file.filename or "", file.content_type, data)
    return studios.studio_view(updated)


@router.get("/studios/{slug}/team")
async def get_team(ctx: StudioOwner):
    return await team.team_view(ctx.studio)


@router.post("/studios/{slug}/invitations")
async def invite(req: InviteRequest, ctx: StudioOwner, request: Request):
    return await team.invite(ctx.studio, ctx.user, req.email, public_base_url(request))


@router.delete("/studios/{slug}/invitations/{invitation_id}")
async def revoke(invitation_id: str, ctx: StudioOwner):
    return await team.revoke(ctx.studio, ctx.user, invitation_id)


@router.delete("/studios/{slug}/members/{membership_id}")
async def remove_member(membership_id: str, ctx: StudioOwner):
    return await team.remove(ctx.studio, ctx.user, membership_id)


@router.get("/studios/{slug}/audit")
async def studio_audit(ctx: StudioOwner):
    return await audit.list_for_studio(ctx.studio.id)


@router.get("/me/invitations")
async def my_invitations(user: CurrentUser):
    return await team.my_invitations(user)


@router.post("/me/invitations/{invitation_id}/accept")
async def accept(invitation_id: str, user: CurrentUser):
    return await team.accept(user, invitation_id)


@router.post("/me/invitations/{invitation_id}/decline")
async def decline(invitation_id: str, user: CurrentUser):
    return await team.decline(user, invitation_id)
