import re
from typing import Annotated

from pydantic import AfterValidator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z0-9-]{2,}$")


def _email(value: str) -> str:
    value = value.strip().lower()
    if len(value) > 254 or not EMAIL_RE.match(value):
        raise ValueError("Enter a valid email address")
    return value


Email = Annotated[str, AfterValidator(_email)]
