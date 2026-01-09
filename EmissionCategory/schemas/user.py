"""User Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from carbon_api.enums import UserRole


class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    role: Optional[str] = Field(UserRole.EMPLOYEE.value, max_length=50)


class UserCreate(UserBase):
    organization_id: int


class UserResponse(UserBase):
    user_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True
