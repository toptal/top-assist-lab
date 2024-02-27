# ./database/page_manager.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base  # Updated import
import sqlite3
from configuration import sql_file_path
from datetime import datetime, timezone
import json
from functools import wraps
import time
from sqlalchemy.exc import OperationalError, SQLAlchemyError


def retry_on_lock(exception, max_attempts=5, initial_wait=0.5, backoff_factor=2):
    """
    A decorator to retry a database operation in case of a lock.

    Args:
        exception: The exception to catch and retry on.
        max_attempts (int): Maximum number of retry attempts.
        initial_wait (float): Initial wait time between attempts in seconds.
        backoff_factor (int): Factor by which to multiply wait time for each retry.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            wait_time = initial_wait
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if "database is locked" in str(e):
                        print(f"Database is locked, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        attempts += 1
                        wait_time *= backoff_factor
                    else:
                        raise
            raise OperationalError("Maximum retry attempts reached, database still locked.")
        return wrapper
    return decorator


# Define the base class for SQLAlchemy models
Base = declarative_base()


# Define the PageData model
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
    comments = Column(Text)
    last_embedded = Column(DateTime)
    date_pulled_from_confluence = Column(DateTime)
    embed = Column(Text)


class PageProgress(Base):
    """
    SQLAlchemy model for storing Confluence page progress.
    """
    __tablename__ = 'page_progress'
    id = Column(Integer, primary_key=True)
    page_id = Column(String, unique=True)
    processed = Column(Boolean, default=False)
    processed_time = Column(DateTime)


class SlackMessageDeduplication(Base):
    """
    SQLAlchemy model for storing deduplication data for Slack messages to prevent reprocessing.
    """
    __tablename__ = 'slack_message_deduplication'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)  # Identifier for the Slack channel.
    message_ts = Column(String, nullable=False, unique=True)  # Timestamp of the message, unique within a channel.

    def __repr__(self):
        return f"<SlackMessageDeduplication(channel_id='{self.channel_id}', message_ts='{self.message_ts}')>"


def parse_datetime(date_string):
    """
    Convert an ISO format datetime string to a datetime object.

    Args:
    date_string (str): ISO format datetime string.

    Returns:
    datetime: A datetime object.
    """
    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))


@retry_on_lock(OperationalError)
def store_pages_data(space_key, pages_data):
    """
    Store Confluence page data into the database.

    Args:
    space_key (str): The key of the Confluence space.
    pages_data (dict): A dictionary of page data, keyed by page ID.
    """
    with Session() as session:
        for page_id, page_info in pages_data.items():
            created_date = parse_datetime(page_info['createdDate'])
            last_updated = parse_datetime(page_info['lastUpdated'])
            date_pulled_from_confluence = page_info['datePulledFromConfluence']

            new_page = PageData(page_id=page_id,
                                space_key=space_key,
                                title=page_info['title'],
                                author=page_info['author'],
                                createdDate=created_date,
                                lastUpdated=last_updated,
                                content=page_info['content'],
                                comments=page_info['comments'],
                                date_pulled_from_confluence=date_pulled_from_confluence
                                )
            session.add(new_page)
            print(f"Page with ID {page_id} written to database")
        session.commit()


def get_page_ids_missing_embeds():
    """
    Retrieve the page IDs of pages that are missing embeddings.
    :return: A list of page IDs.
    """
    session = Session()
    records = session.query(PageData).filter(
        (PageData.lastUpdated > PageData.last_embedded) |
        (PageData.last_embedded.is_(None))
    ).all()
    page_ids = [record.page_id for record in records]
    session.close()
    return page_ids


def get_all_page_data_from_db(space_key=None):
    """
    Retrieve all page data and embeddings from the database. If a space_key is provided,
    filter the records to only include pages from that specific space.
    :param space_key: Optional; the specific space key to filter pages by.
    :return: Tuple of page_ids (list of page IDs), all_documents (list of document strings), and embeddings (list of embeddings as strings)
    """
    session = Session()

    if space_key:
        records = session.query(PageData).filter(PageData.space_key == space_key).all()
    else:
        records = session.query(PageData).all()

    page_ids = [record.page_id for record in records]
    embeddings = [record.embed for record in records]  # Assuming embed is directly stored as a string
    all_documents = [
        f"Page id: {record.page_id}, space key: {record.space_key}, title: {record.title}, "
        f"author: {record.author}, created date: {record.createdDate}, last updated: {record.lastUpdated}, "
        f"content: {record.content}, comments: {record.comments}"
        for record in records
    ]

    session.close()
    return page_ids, all_documents, embeddings

def get_page_data_from_db():
    """
    Retrieve all page data and embeddings from the database.
    This query filter does the following:
        PageData.lastUpdated > PageData.last_embedded:
            It selects records where the lastUpdated timestamp is more recent than the last_embedded timestamp. This would typically mean that the page has been updated since the last time its embedding was generated and stored.
        PageData.last_embedded.is_(None):
            It selects records where the last_embedded field is None, which likely indicates that an embedding has never been generated for the page.
    :return: Tuple of page_ids (list of page IDs), all_documents (list of document strings), and embeddings (list of embeddings as strings)
    """
    session = Session()
    records = session.query(PageData).filter(
        (PageData.lastUpdated > PageData.last_embedded) |
        (PageData.last_embedded.is_(None))
    ).all()

    page_ids = [record.page_id for record in records]
    embeddings = [record.embed for record in records]  # Assuming embed is directly stored as a string
    all_documents = [
        f"Page id: {record.page_id}, space key: {record.space_key}, title: {record.title}, "
        f"author: {record.author}, created date: {record.createdDate}, last updated: {record.lastUpdated}, "
        f"content: {record.content}, comments: {record.comments}"
        for record in records
    ]

    session.close()
    return page_ids, all_documents, embeddings


@retry_on_lock(OperationalError)
def add_or_update_embed_vector(page_id, embed_vector):
    """
    Add or update the embed vector data for a specific page in the database, and update the last_embedded timestamp.

    Args:
        page_id (str): The ID of the page to update.
        embed_vector: The embed vector data to be added or updated, expected to be a serializable object.
    """
    # Serialize the embed_vector to a JSON string
    embed_vector_json = json.dumps(embed_vector)

    # Initialize the session using a context manager to ensure proper resource management
    with Session() as session:
        try:
            # Find the page by page_id
            page = session.query(PageData).filter_by(page_id=page_id).first()

            if page:
                # Page found, update the embed field and last_embedded timestamp
                page.embed = embed_vector_json
                page.last_embedded = datetime.now(timezone.utc)
                print(f"Embed vector and last_embedded timestamp for page ID {page_id} have been updated.")
            else:
                # Page not found, handle accordingly, possibly by creating a new record or raising an error
                print(f"No page found with ID {page_id}. Consider handling this case as needed.")

            session.commit()  # Commit the changes if all operations above are successful
        except SQLAlchemyError as e:
            session.rollback()  # Rollback the transaction on error
            raise e  # Optionally re-raise the exception to signal failure to the caller


def get_page_data_by_ids(page_ids):
    """
    Retrieve specific page data from the database by page IDs.
    :param page_ids: A list of page IDs to retrieve data for.
    :return: Tuple of all_documents (list of document strings) and page_ids (list of page IDs)
    """
    if not page_ids:
        return [], []

    # Connect to the SQLite database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()

    # Prepare the query with placeholders for page IDs
    placeholders = ','.join('?' for _ in page_ids)
    query = f"SELECT * FROM page_data WHERE page_id IN ({placeholders})"

    # Execute the query with the list of page IDs
    cursor.execute(query, page_ids)
    records = cursor.fetchall()

    # Process each record into a string
    all_documents = []
    retrieved_page_ids = []
    for record in records:
        document = (
            f"Page id: {record[1]}, space key: {record[2]}, title: {record[3]}, "
            f"author: {record[4]}, created date: {record[5]}, last updated: {record[6]}, "
            f"content: {record[7]}, comments: {record[8]}"
        )
        all_documents.append(document)
        retrieved_page_ids.append(record[1])

    # Close the SQLite connection
    conn.close()
    return all_documents, retrieved_page_ids


@retry_on_lock(OperationalError)
def update_embed_date(page_ids):
    """
    Update the last_embedded timestamp in the database for the given page IDs.
    :param page_ids:
    :return:
    """
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()
    current_time = datetime.now()
    for page_id in page_ids:
        cursor.execute("UPDATE page_data SET last_embedded = ? WHERE page_id = ?", (current_time, page_id))
    conn.commit()
    conn.close()
    return True


@retry_on_lock(OperationalError)
def mark_page_as_processed(page_id):
    """
    Mark a page as processed in the database.
    :param page_id:
    :return:
    """
    session = Session()
    current_time = datetime.now()
    record = session.query(PageProgress).filter_by(page_id=page_id).first()
    if not record:
        record = PageProgress(page_id=page_id, processed=True, processed_time=current_time)
        session.add(record)
    else:
        record.processed = True
        record.processed_time = current_time
    session.commit()
    session.close()
    return True


def is_page_processed(page_id, last_updated):
    """
    Check if a page has already been processed.
    :param page_id:
    :param last_updated:
    :return:
    """
    session = Session()
    record = session.query(PageProgress).filter_by(page_id=page_id).first()
    session.close()
    if record and record.processed:
        return last_updated <= record.processed_time
    return False


@retry_on_lock(OperationalError)
def reset_processed_status():
    """
    Reset the processed status of all pages.
    :return:
    """
    session = Session()
    session.query(PageProgress).update({PageProgress.processed: False})
    session.commit()
    session.close()
    return True


def get_last_updated_timestamp(page_id):
    """
    Get the last updated timestamp for a page.
    :param page_id:
    :return:
    """
    session = Session()
    page_record = session.query(PageData).filter_by(page_id=page_id).first()
    session.close()

    if page_record:
        return page_record.lastUpdated
    else:
        return None


# Set up the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a session maker object to manage database sessions
Session = sessionmaker(bind=engine)
session = Session()