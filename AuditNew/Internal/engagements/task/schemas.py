from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    name: Optional[str]
    email: Optional[str]
    date_issued: Optional[datetime]


class ActionOwner(BaseModel):
    name: Optional[str]
    email: Optional[str]


class NewTask(BaseModel):
    title: Optional[str]
    description: Optional[str]
    raised_by: Optional[User]
    action_owner: Optional[List[ActionOwner]]

class ResolveTask(BaseModel):
    resolution_summary: Optional[str]
    resolution_details: Optional[str]
    resolved_by: Optional[User]
    decision: Optional[str]