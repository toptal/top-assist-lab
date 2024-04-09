from datetime import datetime
from models.space_info import SpaceInfo
from database.database import Database


class SpaceManager:
    def __init__(self):
        self.db = Database()

    def add_space_info(self, space_key, space_name, last_import_date):
        """Add a new space to the database."""
        new_space = SpaceInfo(
            space_key=space_key,
            space_name=space_name,
            last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
        )
        self.db.add_object(new_space)

    def update_space_info(self, space_key, last_import_date):
        """Update the last import date of an existing space."""
        with self.db.get_session() as session:
            space = session.query(SpaceInfo).filter_by(space_key=space_key).first()
            if space:
                space.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
                session.commit()
            else:
                print(f"Space with key {space_key} not found.")

    def upsert_space_info(self, space_key, space_name, last_import_date):
        """Insert or update space information based on the existence of the space key."""
        with self.db.get_session() as session:
            existing_space = session.query(SpaceInfo).filter_by(space_key=space_key).first()
            if existing_space:
                # The space exists, update the last import date.
                existing_space.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
                operation = 'Updated'
            else:
                # The space does not exist, create a new record.
                new_space = SpaceInfo(
                    space_key=space_key,
                    space_name=space_name,
                    last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
                )
                session.add(new_space)
                operation = 'Added'
            session.commit()
            return operation
