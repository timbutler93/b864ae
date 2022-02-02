from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, String, Boolean, SmallInteger

from api.database import Base


class Imports(Base):
    """Imports Table for storing metadata"""

    __tablename__ = "imports"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(BigInteger)

    date_uploaded = Column(DateTime(timezone=True), server_default=func.now())

    has_headers = Column(Boolean)
    force = Column(Boolean)

    last_name_index = Column(SmallInteger)
    first_name_index = Column(SmallInteger)
    email_index = Column(SmallInteger)

    total = Column(BigInteger)
    done = Column(BigInteger)

    user_id = Column(BigInteger, ForeignKey("users.id"))

    user = relationship("User", back_populates="imports", foreign_keys=[user_id])
    prospects = relationship("Prospect", back_populates="imports")

    def __repr__(self):
        return f"{self.total} | {self.done}"
