from datetime import datetime
from models.space_info import SpaceInfo
from database.database import get_db_session


def upsert_space_info(space_key, space_name, last_import_date):
    """Create or update space information based on the existence of the space key."""
    with get_db_session() as session:
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
