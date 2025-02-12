from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

from pygments.lexer import default


class User(BaseModel):
    name: str
    telephone: str
    type: str
    email: str
    status: str
    role_id: List[int]
    module_id: List[int]
    id: int
    created_at: datetime

class Role(BaseModel):
    value: str
    label: str

class NewUser(BaseModel):
    name: str
    email: EmailStr
    role_id: List[int] = Field(default=[])
    module_id: List[int] | int = Field(default=1)
    telephone: Optional[str] = None
    type: Optional[str] = Field(default="user")
    password: Optional[str] = Field(default="1234")
    status: Optional[bool] = True



class DeleteUser(BaseModel):
    id: str

class UpdateUser(BaseModel):
    id: int
    role: Optional[int] = None
    name: Optional[str] = None
    telephone: Optional[str] = None
    type: Optional[str] = None
    email: Optional[ EmailStr] = None
    password: Optional[str] = None
    status: Optional[bool] = None

class AddRole(BaseModel):
    user_id: int
    role_id: int

class RemoveRole(BaseModel):
    role_id: int
    user_id: int

class ChangePassword(BaseModel):
    email: EmailStr
    old: str
    new: str
