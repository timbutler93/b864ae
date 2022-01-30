from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic.networks import EmailStr


class Prospect(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    import_id: int

    class Config:
        orm_mode = True


class ProspectCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    import_id: int


class ProspectResponse(BaseModel):
    """One page of prospects"""

    prospects: List[Prospect]
    size: int
    total: int
