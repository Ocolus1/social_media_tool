from typing import Optional
from pydantic import BaseModel
from ninja import Schema


# Models for request data
class RegisterSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UpdateProfileSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class Error(Schema):
    message: str


class Success(Schema):
    message: str
