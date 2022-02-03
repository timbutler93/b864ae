from typing import Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Imports, Prospect
from api.crud import ProspectCrud
from sqlalchemy.sql.functions import func

from random import choice
from string import ascii_letters
from os import getcwd, path, makedirs
from email_validator import validate_email, EmailNotValidError


class ImportCrud:
    @classmethod
    def get_import_data(
        cls,
        db: Session,
        import_id: int,
    ) -> Union[Imports, None]:
        return db.query(Imports).filter(Imports.id == import_id).one_or_none()

    @classmethod
    def add_import_metadata(cls, db: Session, data: schemas.CSVImport) -> Imports:
        imports = Imports(**data)
        db.add(imports)
        db.commit()
        db.refresh(imports)
        return imports

    @classmethod
    def get_process_count(cls, db: Session, id_passed: int) -> Union[Imports, None]:
        result = db.query(Imports).filter(Imports.id == id_passed).one_or_none()
        if result is not None:
            return result

    @classmethod
    def get_prospect_count(
        cls,
        db: Session,
        import_id: int,
    ) -> int:
        return db.query(Prospect).filter(Prospect.import_id == import_id).count()

    @classmethod
    def set_up_import(
        cls,
        db: Session,
        current_user: int,
        info: schemas.Metadata,
        line_num: int,
    ) -> Imports:

        imports = ImportCrud.add_import_metadata(
            db,
            {
                "has_headers": info["has_headers"],
                "force": info["force"],
                "last_name_index": info["last_name_index"],
                "first_name_index": info["first_name_index"],
                "email_index": info["email_index"],
                "file_size": info["file_size"],
                "total": line_num,
                "user_id": current_user,
            },
        )
        db.refresh(imports)
        return imports

    @classmethod
    async def process_csv_import(
        cls,
        db: Session,
        current_user: int,
        info: schemas.Metadata,
        split_lines: list,
        import_obj: Imports,
    ):
        # go through file line by line, split on each line on comma
        for index, l in enumerate(split_lines):
            if index == 0 and info["has_headers"]:
                pass
            else:
                split = l.split(b",")
                try:  # try inside for loop to allow valid rows to be entered/updated
                    # Check to see if prospect exists after checking if email field is valid
                    email_valid = validate_email(
                        split[info["email_index"]].decode("utf-8")
                    )
                    prospect = ProspectCrud.get_prospect_by_email(
                        db, current_user, email_valid.ascii_email
                    )

                    if prospect is None:
                        data = {}
                        if not import_obj.first_name_index:
                            data["first_name"] = None
                        else:
                            data["first_name"] = split[info["first_name_index"]].decode(
                                "utf-8"
                            )

                        if not import_obj.last_name_index:
                            data["last_name"] = None
                        else:
                            data["last_name"] = split[info["last_name_index"]].decode(
                                "utf-8"
                            )
                        data["email"] = email_valid.ascii_email
                        data["import_id"] = import_obj.id
                        ProspectCrud.create_prospect(db, current_user, data)
                    elif info["force"]:
                        # update prospect with new info, including import id
                        prospect.first_name = split[info["first_name_index"]].decode(
                            "utf-8"
                        )
                        prospect.last_name = split[info["last_name_index"]].decode(
                            "utf-8"
                        )
                        prospect.import_id = import_obj.id
                        prospect.updated_at = func.now()
                        db.commit()

                except IndexError:
                    pass
                except EmailNotValidError:
                    pass

    @classmethod
    async def save_csv_file(
        cls,
        db: Session,
        imports: Imports,
        file: bytes,
    ):
        random_str = "".join(choice(ascii_letters) for i in range(20))
        imports.file_name = random_str + ".csv"
        imports.file_path = getcwd() + "/CSV"

        if not path.exists(imports.file_path):
            makedirs(imports.file_path)

        with open(imports.file_path + "/" + imports.file_name, "w") as o:
            o.write(file.decode("utf-8"))
        o.close()
