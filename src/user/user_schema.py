
from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Annotated, Optional

_MaxLen = 255

class Register(BaseModel):
    username: Annotated[str, StringConstraints(max_length=_MaxLen)]
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "atifamaan",
                "email": "atifamaan@gmail.com",
                "password": "12345678",
                "is_active": False
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "atifamaan",
                "email": "atifamaan@gmail.com",
            }
        }


class Login(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "atifamaan@gmail.com",
                "password": "12345678"
            }
        }