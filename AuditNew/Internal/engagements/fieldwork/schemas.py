from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class Section(BaseModel):
    value: str

class User(BaseModel):
    name: Optional[str]
    email: Optional[str]
    date_issued: Optional[datetime]

class ActionOwner(BaseModel):
    name: Optional[str]
    email: Optional[str]

class SummaryReviewNotes(BaseModel):
    reference: Optional[str]
    title: Optional[str]
    description: Optional[str]
    date_raised: Optional[datetime]
    raised_by: Optional[User]
    action_owner: Optional[List[ActionOwner]]
    resolution_summary: Optional[str]
    resolution_details: Optional[str]
    resolved_by: Optional[User]
    date_resolved: Optional[datetime]
    decision: Optional[str]

class SummaryTask(BaseModel):
    reference: Optional[str]
    title: Optional[str]
    description: Optional[str]
    date_raised: Optional[datetime]
    raised_by: Optional[User]
    action_owner: Optional[List[ActionOwner]]
    resolution_summary: Optional[str]
    resolution_details: Optional[str]
    resolved_by: Optional[User]
    date_resolved: Optional[datetime]
    decision: Optional[str]

class SummaryAuditProcedure(BaseModel):
    reference: Optional[str]
    program: Optional[str]
    title: Optional[str]
    prepared_by: Optional[User]
    reviewed_by: Optional[User]
    effectiveness: Optional[str]
    issue_count: Optional[int]