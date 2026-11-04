from datetime import datetime, timezone
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BaseDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: PyObjectId | None = Field(default=None, validation_alias="_id")

    def to_mongo(self) -> dict[str, Any]:
        data = self.model_dump(exclude={"id"})
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_mongo(cls, doc: dict[str, Any] | None):
        return cls.model_validate(doc) if doc else None
