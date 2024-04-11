from datetime import datetime
import logging

from database.page_manager import PageManager
from database.space_manager import SpaceManager
import vector.pages

from .client import ConfluenceClient
from .retriever import retrieve_space

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def tui_choose_space():
    """
    Prompt the user to choose a Confluence space from a list of available spaces.

    Returns:
    str: The key of the chosen Confluence space.
    """
    client = ConfluenceClient()
    spaces = client.retrieve_space_list()
    for i, space in enumerate(spaces):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces[choice]['key'], spaces[choice]['name']


def import_space(space_key, space_name):
    import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    pages = retrieve_space(space_key)
    PageManager().store_pages_data(space_key, pages)

    vector.pages.generate_missing_embeddings_to_database()

    SpaceManager().upsert_space_info(
        space_key=space_key,
        space_name=space_name,
        last_import_date=import_date
    )

    vector.pages.import_from_database(space_key)
