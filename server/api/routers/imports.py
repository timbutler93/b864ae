from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectCrud, ImportCrud
from api.models import Imports
import os
router = APIRouter(prefix="/api", tags=["imports"])

@router.get("/prospects_files/{id}/progress", response_model=schemas.CSVTrackResponse)
async def get_import_status(
            id: int, 
            db: Session = Depends(get_db),
            current_user: schemas.User = Depends(get_current_user)
            ):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
                )
            
            result = ImportCrud.get_process_count(db, id)
            
            if current_user.id != result.user_id:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    detail=f"You do not have access to that import's status",
                )
            
            return {"total": result.total, "done": result.done}

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
        
    filesize = os.fstat(file.file.fileno()).st_size #get file size
    fileRead = file.file.read()
    splitlines = fileRead.splitlines()
    #if has_headers is true, subtract 1 row from num lines
    if has_headers:
        size = len(splitlines) - 1
    else:
        size = len(splitlines)  
            
    metadata = { 
                    "email_index" : email_index, 
                    "first_name_index": first_name_index, 
                    "last_name_index": last_name_index, 
                    "force": force, 
                    "has_headers": has_headers,
                    "file_size": filesize,
                    "user_id": current_user.id
                }
    imports = ImportCrud.set_up_import(db, current_user.id, metadata, size)
    await ImportCrud.save_csv_file(db, imports, fileRead)
    await ImportCrud.process_csv_import(db, current_user.id, metadata, splitlines, imports)
    
    return {"id": imports.id}
