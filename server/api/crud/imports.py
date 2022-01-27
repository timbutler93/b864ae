from typing import Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Imports
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectCrud
from fastapi import HTTPException, status
class ImportCrud:
    @classmethod
    def get_import_data(
        cls, 
        db: Session, 
        importID: int,
        ) -> Union[Imports, None]:
        return db.query(Imports).filter(Imports.id == importID).one_or_none()
        
    @classmethod
    def add_import_metadata(
        cls,
        db: Session,
        data: schemas.CSVImport
        ) -> Imports:
        imports = Imports(**data)
        db.add(imports)
        db.commit()
        db.refresh(imports)
        return imports
    
    @classmethod
    def get_metadata_count(
        cls,
        db: Session,
        ) -> int:
        return db.query(Imports).count()
    
    def get_process_count(
        cls,
        db: Session,
        idPassed: int
        ) -> Union[dict, None]:
        result = db.query(Imports).filter(Imports.id == idPassed).one_or_none()
        if result is not None:
            return result

    async def process_csv_import(
        db: Session,
        current_user: int,
        info: schemas.Metadata,
        file: bytes,
        ) -> Imports:
        splitlines = file.splitlines()
        
        if info['has_headers'] == True:
            size = len(splitlines) - 1
        else:
            size = len(splitlines)
            
        imports = ImportCrud.add_import_metadata(db, {"has_headers": info['has_headers'], "force": info['force'], "last_name_index": info['last_name_index'], "first_name_index": info['first_name_index'], "email_index": info['email_index'], "total": size, "done": 0})
        db.refresh(imports)
        print(ImportCrud.get_metadata_count(db)) #for debugging
        
        for index, l in enumerate(splitlines):
            if index == 0 and info['has_headers'] == True:
                pass
            else:
                split = l.split(b",") 
                prospect = ProspectCrud.get_prospect_by_email(db, current_user.id, split[info['email_index']].decode('utf-8'));
                imports.done += 1
                if prospect is None:
                    ProspectCrud.create_prospect(db, current_user.id, {"email" : split[info['email_index']].decode('utf-8'), "first_name": split[info['first_name_index']].decode('utf-8'), "last_name" : split[info['last_name_index']].decode('utf-8') })
                elif(info['force'] == True):
                    prospect.first_name = split[info['first_name_index']].decode('utf-8')
                    prospect.last_name = split[info['last_name_index']].decode('utf-8')
                    
                db.commit()
            
        return imports
        