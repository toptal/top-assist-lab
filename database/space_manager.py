from datetime import datetime
from models.space_info import SpaceInfo


class SpaceManager:
    def __init__(self):
        pass

    def add_space_info(self, space_key, space_name, last_import_date, session):
        """Add a new space to the database."""
        new_space = SpaceInfo(
            space_key=space_key,
            space_name=space_name,
            last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
        )
        session.add(new_space)
        session.commit()

    def update_space_info(self, space_key, last_import_date, session):
        """Update the last import date of an existing space."""
        space = session.query(SpaceInfo).filter_by(space_key=space_key).first()

        if space:
            space.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            session.commit()
        else:
            print(f"Space with key {space_key} not found.")

    def upsert_space_info(self, session, space_key, space_name, last_import_date):
        """Create or update space information based on the existence of the space key."""
        existing_space = session.query(SpaceInfo).filter_by(space_key=space_key).first()
        last_import_date_formatted = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')

        if existing_space:
            existing_space.last_import_date = last_import_date_formatted
        else:
            new_space = SpaceInfo(
                space_key=space_key,
                space_name=space_name,
                last_import_date=last_import_date_formatted
            )
            session.add(new_space)
        session.commit()
