from datetime import datetime
from models.space_info import SpaceInfo


class SpaceManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def add_space_info(self, space_key, space_name, last_import_date):
        """Add a new space to the database."""
        with self.db_session as session:
            SpaceInfo().create_or_update(
                session,
                space_key=space_key,
                space_name=space_name,
                last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            )

    def update_space_info(self, space_key, last_import_date):
        """Update the last import date of an existing space."""
        with self.db_session as session:
            SpaceInfo().create_or_update(session, space_key=space_key, last_import_date=last_import_date)
            print(f"Space with key {space_key} updated")

    def upsert_space_info(self, space_key, space_name, last_import_date):
        """Create or update space information based on the existence of the space key."""
        with self.db_session as session:
            SpaceInfo().create_or_update(session,
                                         space_key=space_key,
                                         space_name=space_name,
                                         last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
                                         )
