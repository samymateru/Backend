from pydantic import BaseModel
from typing import Optional

class Control(BaseModel):
    id: Optional[int] = None
    ref: Optional[str]
    name: Optional[str]
    objective: Optional[str]
    type: Optional[str]