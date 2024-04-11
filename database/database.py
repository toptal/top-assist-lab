from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configuration import db_url
from models.bookmarked_conversation import BookmarkedConversation
from models.page_data import PageData
from models.qa_interaction import QAInteraction
from models.quiz_question import QuizQuestion
from models.space_info import SpaceInfo
from models.user_score import UserScore
from contextlib import contextmanager

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# TODO: Extract and uncomment
for model in [QAInteraction, SpaceInfo, PageData, BookmarkedConversation, QuizQuestion, UserScore]:
    model.metadata.create_all(engine)
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
