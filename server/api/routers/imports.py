from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ImportCrud
from api.models import Imports
from os import fstat
from typing import Optional

router = APIRouter(prefix="/api", tags=["imports"])


@router.get("/prospects_files/{id}/progress", response_model=schemas.CSVTrackResponse)
async def get_import_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    result = ImportCrud.get_process_count(db, id)
    if not result:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Import with id {id} does not exist",
        )
    if current_user.id != result.user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"You do not have access to that import's status",
        )

    return {"total": result.total, "done": ImportCrud.get_prospect_count(db, id)}


@router.post("/prospects_files/import", response_model=schemas.CSVUploadResponse)
async def upload_prospect_file(
    file: UploadFile = File(...),
    email_index: int = Form(...),
    first_name_index: Optional[int] = Form(None),
    last_name_index: Optional[int] = Form(None),
    force: Optional[bool] = Form(False),
    has_headers: Optional[bool] = Form(False),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )

    file_size = fstat(file.file.fileno()).st_size  # get file size
    file_read = file.file.read()
    split_lines = file_read.splitlines()

    # if has_headers is true, subtract 1 row from num lines
    if has_headers:
        size = len(split_lines) - 1
    else:
        size = len(split_lines)

    metadata = {
        "email_index": email_index,
        "first_name_index": first_name_index,
        "last_name_index": last_name_index,
        "force": force,
        "has_headers": has_headers,
        "file_size": file_size,
        "user_id": current_user.id,
    }
    imports = ImportCrud.set_up_import(db, current_user.id, metadata, size)
    await ImportCrud.save_csv_file(db, imports, file_read)
    await ImportCrud.process_csv_import(
        db, current_user.id, metadata, split_lines, imports
    )

    return {"id": imports.id}
