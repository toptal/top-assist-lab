
import logging
from typing import List

from configuration import embedding_model_id, vector_collection_interactions
from open_ai.embedding.embed_manager import embed_text

from ..chroma import get_client


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def retrieve_relevant_ids(query: str, count: int) -> List[int]:
    """
    Retrieve the most relevant interactions for a given query using vector database.

    Args:
        query (str): The query to retrieve relevant interactions for.

    Returns:
        List[str]: A list of interaction IDs of the most relevant interactions.
    """

    # Generate the query embedding using OpenAI
    try:
        query_embedding = embed_text(text=query, model=embedding_model_id)
    except Exception as e:
        logging.error(f"Error generating query embedding: {e}")
        return []

    # Initialize the ChromaDB client
    client = get_client()
    collection = client.get_collection(vector_collection_interactions)

    # Perform a similarity search in the collection
    similar_items = collection.query(
        query_embeddings=[query_embedding],
        n_results=count
    )

    # Extract and return the interaction IDs from the results
    if 'ids' in similar_items:
        interaction_ids = [id for sublist in similar_items['ids'] for id in sublist]
    else:
        logging.warning("No 'ids' key found in similar_items, no interactions retrieved.")
        interaction_ids = []

    return interaction_ids
