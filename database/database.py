from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configuration import DB_URL
from contextlib import contextmanager

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


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
