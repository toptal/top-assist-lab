# from database.database import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from database.mixins.crud_mixin import CRUDMixin
from sqlalchemy import Column, Integer, String, Text, DateTime
import json  # TODO Can we switch to sqlalchemy JSON type?



class PageData(Base):
    """
    SQLAlchemy model for storing Confluence page data.
    """
    __tablename__ = 'page_data'

    id = Column(Integer, primary_key=True)
    page_id = Column(String)
    space_key = Column(String)
    title = Column(String)
    author = Column(String)
    createdDate = Column(DateTime)
    lastUpdated = Column(DateTime)
    content = Column(Text)
    comments = Column(Text, default=json.dumps([]))
    last_embedded = Column(DateTime)
    embed = Column(Text, default=json.dumps([]))

