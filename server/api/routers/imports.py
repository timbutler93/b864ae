from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectCrud

router = APIRouter(prefix="/api", tags=["imports"])

@router.post("/prospects_files/import", response_model=schemas.CSVUploadResponse)
async def upload_prospect_file(
    email_index: int = Form(...),
    first_name_index: int = Form(...),
    last_name_index: int = Form(...),
    force: bool = Form(...),
    has_headers: bool = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
  
    fileRead = file.file.read()
    splitlines = fileRead.splitlines()
    
    for index, l in enumerate(splitlines):
        if index == 0 and has_headers == True:
            pass
        else:
            split = l.split(b",")
            ProspectCrud.create_prospect(db, current_user.id, {"email" : split[email_index].decode('utf-8'), "first_name": split[first_name_index].decode('utf-8'), "last_name" : split[last_name_index].decode('utf-8') })
    '''Temporary return for testing'''
    return {"status" : 1 } 