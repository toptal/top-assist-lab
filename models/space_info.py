from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class SpaceInfo(Base):
    """
    SQLAlchemy model for storing Confluence space data.
    """
    __tablename__ = 'space_info'

    id = Column(Integer, primary_key=True)
    space_key = Column(String, nullable=False)
    space_name = Column(String, nullable=False)
    last_import_date = Column(DateTime, nullable=False)
