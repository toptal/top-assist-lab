# ./database/nur_database.py
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from models.page_data import PageData
from database.database import Database
from datetime import datetime, timezone
import json


class PageManager:
    def __init__(self):
        self.db = Database()

    def parse_datetime(self, date_string):
        """
        Convert an ISO format datetime string to a datetime object.

        Args:
        date_string (str): ISO format datetime string.

        Returns:
        datetime: A datetime object.
        """
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))

    def store_pages_data(self, space_key, pages):
        """
        Store Confluence page data into the database.

        Args:
        space_key (str): The key of the Confluence space.
        pages (list): A list of page data
        """
        for page in pages:
            page_id = page['id']
            new_page = PageData(page_id=page_id,
                                space_key=space_key,
                                title=page['title'],
                                author=page['author'],
                                createdDate=self.parse_datetime(page['createdDate']),
                                lastUpdated=self.parse_datetime(page['lastUpdated']),
                                content=page['content'],
                                comments=page['comments']
                                )
            self.db.add_object(new_page)
            print(f"Page with ID {page_id} written to database")

    def get_page_ids_missing_embeds(self):
        """
        Retrieve the page IDs of pages that are missing embeddings.
        :return: A list of page IDs.
        """
        with self.db.get_session() as session:
            records = session.query(PageData).filter(
                (PageData.lastUpdated > PageData.last_embedded) |
                (PageData.last_embedded.is_(None))
            ).all()
            page_ids = [record.page_id for record in records]
            return page_ids

    def get_all_page_data_from_db(self, space_key=None):
        """
        Retrieve all page data and embeddings from the database. If a space_key is provided,
        filter the records to only include pages from that specific space.
        :param space_key: Optional; the specific space key to filter pages by.
        :return: Tuple of page_ids (list of page IDs), all_documents (list of document strings), and embeddings (list of embeddings as strings)
        """
        with self.db.get_session() as session:

            if space_key:
                records = session.query(PageData).filter(PageData.space_key == space_key).all()
            else:
                records = session.query(PageData).all()

            formatted = self.format_page_data(records)
            return formatted

    def get_page_data_from_db(self):
        """
        Retrieve all page data and embeddings from the database.
        This query filter does the following:
            PageData.lastUpdated > PageData.last_embedded:
                It selects records where the lastUpdated timestamp is more recent than the last_embedded timestamp. This would typically mean that the page has been updated since the last time its embedding was generated and stored.
            PageData.last_embedded.is_(None):
                It selects records where the last_embedded field is None, which likely indicates that an embedding has never been generated for the page.
        :return: Tuple of page_ids (list of page IDs), all_documents (list of document strings), and embeddings (list of embeddings as strings)
        """
        with self.db.get_session() as session:
            records = session.query(PageData).filter(
                (PageData.lastUpdated > PageData.last_embedded) |
                (PageData.last_embedded.is_(None))
            ).all()

            formatted = self.format_page_data(records)
            return formatted

    @staticmethod
    def format_page_data(records):
        page_ids = [record.page_id for record in records]
        embeddings = [record.embed for record in records]  # Assuming embed is directly stored as a string
        all_documents = [
            f"Page id: {record.page_id}, space key: {record.space_key}, title: {record.title}, "
            f"author: {record.author}, created date: {record.createdDate}, last updated: {record.lastUpdated}, "
            f"content: {record.content}, comments: {record.comments}"
            for record in records
        ]
        return page_ids, all_documents, embeddings

    def add_or_update_embed_vector(self, page_id, embed_vector):
        """
        Add or update the embed vector data for a specific page in the database, and update the last_embedded timestamp.

        Args:
            page_id (str): The ID of the page to update.
            embed_vector: The embed vector data to be added or updated, expected to be a list of floats.
        """
        # Serialize the embed_vector to a JSON string here
        embed_vector_json = json.dumps(embed_vector)

        with self.db.get_session() as session:
            try:
                page = session.query(PageData).filter_by(page_id=page_id).first()

                if page:
                    page.embed = embed_vector_json  # Store the serialized list
                    page.last_embedded = datetime.now(timezone.utc)
                    print(f"Embed vector and last_embedded timestamp for page ID {page_id} have been updated.")
                else:
                    print(f"No page found with ID {page_id}. Consider handling this case as needed.")

                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                raise e

    def get_page_data_by_ids(self, page_ids):
        """
        Retrieve specific page data from the database by page IDs.
        :param page_ids: A list of page IDs to retrieve data for.
        :return: Tuple of all_documents (list of document strings) and page_ids (list of page IDs)
        """
        if not page_ids:
            return [], []

        try:
            with self.db.get_session() as session:
                page_data_records = session.query(PageData).filter(PageData.page_id.in_(page_ids)).all()

                all_documents = []
                retrieved_page_ids = []
                for record in page_data_records:
                    document = (
                        f"Page id: {record.page_id}, space key: {record.space_key}, title: {record.title}, "
                        f"author: {record.author}, created date: {record.createdDate}, last updated: {record.lastUpdated}, "
                        f"content: {record.content}, comments: {record.comments}"
                    )
                    all_documents.append(document)
                    retrieved_page_ids.append(record.page_id)

                return all_documents, retrieved_page_ids
        except SQLAlchemyError as e:
            print(f"Error retrieving page data by IDs: {e}")
            return [], []

    def update_embed_date(self, page_ids):
        """
        Update the last_embedded timestamp in the database for the given page IDs.
        :param page_ids:
        :return:
        """
        try:
            with self.db.get_session() as session:
                current_time = datetime.now()
                for page_id in page_ids:
                    session.query(PageData).filter_by(page_id=page_id).update({'last_embedded': current_time})
                session.commit()
                return True
        except SQLAlchemyError as e:
            print(f"Error updating embed date: {e}")
            self.db.rollback()
            return False

    def find_page(self, page_id) -> Optional[PageData]:
        """
        Find a page in the database by its ID.
        :param page_id: The ID of the page to find.
        :return: The page data if found, or None if not found.
        """
        with self.db.get_session() as session:
            page_record = session.query(PageData).filter_by(page_id=page_id).first()
            return page_record

    def find_pages(self, page_ids) -> List[PageData]:
        """
        Find multiple pages in the database by their IDs.
        :param page_ids: A list of page IDs to find.
        :return: A list of page data if found, or an empty list if not found.
        """
        with self.db.get_session() as session:
            pages = session.query(PageData).filter(PageData.page_id.in_(page_ids)).all()
            return pages

    def format_page_for_llm(self, page: PageData) -> str:
        """
        Format a page for use with the LLM.
        :param page: The page data.
        :return: The formatted page content as a string.
        """
        page_data = {
            'spaceKey': page.space_key,
            'pageId': page.page_id,
            'title': page.title,
            'author': page.author,
            'createdDate': page.createdDate,
            'lastUpdated': page.lastUpdated,
            'content': page.content,
            'comments': page.comments
        }

        content = ""
        for key, value in page_data.items():
            content += f"{key}: {value}\n"
        return content
