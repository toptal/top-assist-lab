import json
import logging

from configuration import vector_collection_pages
from database.page_manager import PageManager

from ..chroma import get_client


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_data(space_key):
    page_ids, _, embeddings = PageManager().get_all_page_data_from_db(space_key=space_key)

    # Deserialize the embeddings and filter out None values
    valid_embeddings, valid_page_ids = [], []
    for i, embed in enumerate(embeddings):
        if embed is None:
            logging.warning(f"Skipping embedding at index {i}: Embed is None")
            continue

        try:
            # Deserialize the JSON string into a Python list
            deserialized_embed = json.loads(embed)
            valid_embeddings.append(deserialized_embed)
            valid_page_ids.append(page_ids[i])
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Failed to deserialize embedding at index {i}: {e}")
            continue

        if i % 10 == 0:
            logging.info(f"Processed {i + 1}/{len(embeddings)} embeddings.")

    logging.info("Completed deserializing all embeddings.")
    return valid_page_ids, valid_embeddings


def insert_data(ids, embeddings):
    collection_name = vector_collection_pages
    logging.info(f"Ensuring collection '{collection_name}' exists...")
    client = get_client()
    collection = client.get_or_create_collection(collection_name)

    # Add embeddings to the collection
    logging.info(f"Adding {len(embeddings)} embeddings to the collection '{collection_name}'...")
    try:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=[{"page_id": pid} for pid in ids]
        )
        logging.info(f"Successfully added {len(embeddings)} embeddings to the collection '{collection_name}'.")
        logging.info(f"Collection count {collection.count()} ")

    except Exception as e:
        logging.error(f"Error adding pages to the collection: {e}")

    logging.info(f"Embeddings added to {collection_name} collection.")


def import_from_database(space_key=None):
    """
    Extracts embeddings from the database and inserts them into the vector database.
    Args:
        space_key (str): The space key for the Confluence space to import data from.
    """
    ids, embeddings = extract_data(space_key)
    insert_data(ids, embeddings)
