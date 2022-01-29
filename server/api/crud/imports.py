from typing import Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Imports
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.crud import ProspectCrud

import random
import string
import os

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
        
    @classmethod
    def get_process_count(
        cls,
        db: Session,
        idPassed: int
        ) -> Union[dict, None]:
        result = db.query(Imports).filter(Imports.id == idPassed).one_or_none()
        if result is not None:
            return result
            
    @classmethod        
    def set_up_import(
        cls,
        db: Session,
        current_user: int,
        info: schemas.Metadata,
        file: bytes,
    ) -> Imports:
        splitlines = file.splitlines()
        #if has_headers is true, subtract 1 row from num lines
        if info['has_headers'] == True:
            size = len(splitlines) - 1
        else:
            size = len(splitlines)
            
        imports = ImportCrud.add_import_metadata(db, 
                                                    {
                                                        "has_headers": info['has_headers'], 
                                                        "force": info['force'], 
                                                        "last_name_index": info['last_name_index'], 
                                                        "first_name_index": info['first_name_index'], 
                                                        "email_index": info['email_index'], 
                                                        "file_size": info['file_size'],
                                                        "total": size, 
                                                        "done": 0
                                                    }
                                                )
        db.refresh(imports)
        return imports
        
    @classmethod
    async def process_csv_import(
        cls,
        db: Session,
        current_user: int,
        info: schemas.Metadata,
        file: bytes,
        importObj: Imports,
        ) -> Imports:
        splitlines = file.splitlines()
        #go through file line by line, split on each line on comma
        for index, l in enumerate(splitlines):
            if index == 0 and info['has_headers']:
                pass
            else:
                split = l.split(b",") 
                try: #try inside for loop to allow valid rows to be entered/updated
                #Check to see if prospect exists
                    prospect = ProspectCrud.get_prospect_by_email(db, current_user.id, split[info['email_index']].decode('utf-8'));
                    
                    if prospect is None:
                        ProspectCrud.create_prospect(db, 
                                                    current_user.id, 
                                                        {
                                                        "email" : split[info['email_index']].decode('utf-8'), 
                                                        "first_name": split[info['first_name_index']].decode('utf-8'), 
                                                        "last_name" : split[info['last_name_index']].decode('utf-8') 
                                                        }
                                                    )
                    elif(info['force']):
                        prospect.first_name = split[info['first_name_index']].decode('utf-8')
                        prospect.last_name = split[info['last_name_index']].decode('utf-8')
                    importObj.done += 1    
                    db.commit()
                except IndexError:
                    print('Index out of bounds')
                    pass
        return importObj
        
    @classmethod
    async def save_csv_file(
        cls,
        db: Session,
        imports: Imports,
        file: bytes,
        ) -> Imports:
        randomStr = ''.join(random.choice(string.ascii_letters) for i in range(20))
        imports.file_name = randomStr + ".csv"
        imports.file_path = os.getcwd()
        with open(imports.file_name, 'w') as o:
            o.write(file.decode('utf'))
        o.close()
      
        return imports