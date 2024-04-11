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

    def upsert_space_info(self, space_key, space_name, last_import_date, session):
        """Create or update space information based on the existence of the space key."""
        session = session.query(SpaceInfo).filter_by(space_key=space_key).first()

        if session:
            session.space_name = space_name
            session.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            print(f"Space with key {space_key} updated")
        else:
            session.add(SpaceInfo(space_key=space_key, space_name=space_name, last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')))
            print(f"Space with key {space_key} created")
        session.commit()
