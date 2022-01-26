from pydantic import BaseModel

class CSVUploadResponse(BaseModel):
    status: int

class CSVTrackResponse(BaseModel):
    total: int
    done: int
    