from pydantic import BaseModel
from datetime import datetime

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
    has_header: bool
    force: bool
    email_index: int
    first_name_index: int
    last_name_index: int
    
class Metadata(BaseModel):
    has_headers: bool
    force: bool
    email_index: int
    first_name_index: int
    last_name_index: int
    