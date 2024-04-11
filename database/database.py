from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/main_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()


def get_db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from configuration import db_url
from models.qa_interaction import QAInteraction
from models.space_info import SpaceInfo
from models.page_data import PageData
from models.bookmarked_conversation import BookmarkedConversation
from models.quiz_question import QuizQuestion
from models.user_score import UserScore


class Database:
    """
    Class providing access to a SQLAlchemy database.

    This class implements the Singleton pattern for creating and managing a connection to a SQLAlchemy database.
    It provides methods for getting database sessions and accessing the SQLAlchemy Engine object.

    Attributes:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy Engine object representing the connection to the database.
        Session (sqlalchemy.orm.Session): The SQLAlchemy session factory used for creating database sessions.
    """

    _instance = None

    def __new__(cls):
        """
        Create a new instance of the Database class.

        If an instance of the class has not been created yet, it is created; otherwise, the existing instance is returned.

        Returns:
            Database: An instance of the Database class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_engine()
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        """
        Create tables in the database if they do not exist.
        """
        for model in [QAInteraction, SpaceInfo, PageData, BookmarkedConversation, QuizQuestion, UserScore]:
            model.metadata.create_all(self.engine)

    def _init_engine(self):
        """
        Initialize the SQLAlchemy Engine object and session factory.

        Creates the Engine object for connecting to the database and the session factory for creating database sessions.
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """
        Get a new database session.

        Returns:
            sqlalchemy.orm.Session: A new database session.
        """
        return self.Session()

    def add_object(self, obj):
        """
        Adds the given object to the database.

        Args:
            obj: The object to add to the database.

        Returns:
            int or None: The ID of the added object if successful, None otherwise.

        Raises:
            None

        """
        try:
            with self.get_session() as session:
                session.add(obj)
                session.commit()
                return obj
        except SQLAlchemyError as e:
            class_name = obj.__class__.__name__
            print(f"Error adding object of type {class_name}: {e}")
            session.rollback()
            return None
