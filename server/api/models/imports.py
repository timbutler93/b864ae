from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, String, Boolean, SmallInteger

from api.database import Base


class Imports(Base):
    """Imports Table for storing metadata"""

    __tablename__ = "imports"

    id = Column(BigInteger, primary_key=True, index=True)
    size = Column(BigInteger)
    file_name = Column(String)
    file_path = Column(String)
    
    date_uploaded = Column(DateTime(timezone=True), server_default=func.now())
    
    has_headers = Column(Boolean)
    force = Column(Boolean)
    
    last_name_index = Column(SmallInteger)
    first_name_index = Column(SmallInteger)
    email_index = Column(SmallInteger)

    def __repr__(self):
        return f"{self.id} | {self.has_headers}"
