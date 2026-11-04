from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from services import email

router = APIRouter(prefix="/api/poc", tags=["poc-email"])


class TestEmailRequest(BaseModel):
    to: EmailStr


@router.post("/email/test")
async def send_test_email(req: TestEmailRequest):
    # Fixed server-side template; recipient restricted to an env allowlist (no open relay).
    if req.to.lower() not in email.allowed_test_recipients():
        raise HTTPException(403, "Recipient not in POC_EMAIL_ALLOWED_RECIPIENTS allowlist")
    return {"message_id": await email.send_test_email(req.to), "to": req.to}
