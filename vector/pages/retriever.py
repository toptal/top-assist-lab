import logging
from typing import List

from configuration import embedding_model_id, vector_collection_pages
from open_ai.embedding.embed_manager import embed_text

from ..chroma import get_client


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def retrieve_relevant_ids(question: str, count: int) -> List[int]:
    """
    Retrieve the most relevant documents for a given question using the vector database.

    Args:
        question (str): The question to retrieve relevant documents for.

    Returns:
        List[str]: A list of document IDs of the most relevant documents.
    """

    try:
        query_embedding = embed_text(text=question, model=embedding_model_id)
    except Exception as e:
        logging.error(f"Error generating query embedding: {e}")
        return []

    client = get_client()
    collection = client.get_collection(vector_collection_pages)
    similar_items = collection.query(
        query_embeddings=[query_embedding],  # Now passing the actual list of embeddings
        n_results=count
    )

    # Extract and return the document IDs from the results
    if 'ids' in similar_items:
        page_ids = [int(id) for sublist in similar_items['ids'] for id in sublist]
    else:
        logging.warning("No 'ids' key found in similar_items, no documents retrieved.")
        page_ids = []

    return page_ids
