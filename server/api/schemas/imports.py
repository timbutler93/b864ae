from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CSVUploadResponse(BaseModel):
    id: int

class CSVTrackResponse(BaseModel):
    total: int
    done: int
    
    class Config:
        orm_mode = True

    
class CSVImport(BaseModel):
    id: int
    size: int
    date_uploaded: datetime
    has_headers: Optional[bool] = False
    force: Optional[bool] = False
    email_index: int
    first_name_index: Optional[int] = None
    last_name_index: Optional[int] = None
    user_id: int
    
class Metadata(BaseModel):
    has_headers: Optional[bool] = False
    force: Optional[bool] = False
    email_index: int
    first_name_index: Optional[int] = None
    last_name_index: Optional[int] = None
