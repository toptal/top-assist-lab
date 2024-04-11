# from database.database import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from database.mixins.crud_mixin import CRUDMixin
from sqlalchemy import Column, Integer, String, DateTime


class SpaceInfo(Base, CRUDMixin):
    """
    SQLAlchemy model for storing Confluence space data.
    """
    __tablename__ = 'space_info'

    id = Column(Integer, primary_key=True)
    space_key = Column(String, nullable=False)
    space_name = Column(String, nullable=False)
    last_import_date = Column(DateTime, nullable=False)

    def get_filter_attributes(self):
        return [
            "id", "space_key"
        ]
