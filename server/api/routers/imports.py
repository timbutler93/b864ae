from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectCrud, ImportCrud
from api.models import Imports

router = APIRouter(prefix="/api", tags=["imports"])

@router.get("/prospects_files/{id}/progress", response_model=schemas.CSVTrackResponse)
async def get_import_status(
            id: int, 
            db: Session = Depends(get_db),
            current_user: schemas.User = Depends(get_current_user)
            ):
            print(id)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
                )
            
            result = ImportCrud.get_process_count(current_user, db, id)
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
    
    fileRead = file.file.read()
    metadata = { "email_index" : email_index, "first_name_index": first_name_index, "last_name_index": last_name_index, "force": force, "has_headers": has_headers}
    
    imports = await ImportCrud.process_csv_import(db, current_user, metadata, fileRead);
    '''Temporary return for testing'''
    return {"status": imports.id}
