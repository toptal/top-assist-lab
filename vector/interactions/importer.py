import json
import logging

from configuration import vector_collection_interactions
from database.interaction_manager import QAInteractionManager
from database.database import get_db_session

from ..chroma import get_client


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_data():
    with get_db_session() as session:
        interactions = QAInteractionManager().get_interactions_with_embeds(session)
        ids, embeddings = [], []
        # Deserialize the embeddings and filter out None values
        for i, interaction in enumerate(interactions):
            if interaction.embed is None:
                logging.warning(f"Skipping embedding at index {i}: Embed is None")
                continue

            try:
                # Deserialize the JSON string into a Python list
                embeddings.append(json.loads(interaction.embed))
                ids.append(str(interaction.id))
            except (json.JSONDecodeError, TypeError) as e:
                logging.error(f"Failed to deserialize embedding at index {i}: {e}")
                continue

            if i % 10 == 0:
                logging.info(f"Processed {i + 1}/{len(embeddings)} embeddings.")

        logging.info("Completed deserializing all embeddings.")
        return ids, embeddings


def insert_data(ids, embeddings):
    collection_name = vector_collection_interactions
    logging.info(f"Ensuring collection '{collection_name}' exists...")
    client = get_client()
    collection = client.get_or_create_collection(collection_name)

    # Add interactions to the collection
    logging.info(f"Adding {len(embeddings)} interactions to the collection '{collection_name}'...")
    try:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=[{"interaction_id": iid} for iid in ids]
        )
        logging.info(f"Successfully added {len(embeddings)} interactions to the collection '{collection_name}'.")
        logging.info(f"Collection count {collection.count()} ")

    except Exception as e:
        logging.error(f"Error adding interactions to the collection: {e}")

    logging.info(f"Embeddings added to {collection_name} collection.")


def import_from_database():
    ids, embeddings = extract_data()
    insert_data(ids, embeddings)
