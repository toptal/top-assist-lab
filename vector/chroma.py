# Import necessary modules and functions
from configuration import pages_collection_name, vector_folder_path, embedding_model_id, document_count
import chromadb
import logging
from typing import List
from open_ai.embedding.embed_manager import embed_text
from database.page_manager import PageManager


def generate_document_embedding(page_id, page_content, model=embedding_model_id):
    """
    Generates an embedding for the given text using the specified OpenAI model.
    Returns a tuple of (embedding, error_message).
    """
    # Ensure the content does not exceed the maximum token limit
    page_content = page_content[:8190]

    try:
        # embed_text now returns a serialized JSON string of the embedding vector
        embedding_json = embed_text(text=page_content, model=model)
        return embedding_json, None
    except Exception as e:
        error_message = f"Error generating embedding for page ID {page_id}: {e}\n"
        logging.error(error_message)
        return None, error_message


def retrieve_relevant_documents(question: str) -> List[str]:
    """
    Retrieve the most relevant documents for a given question using ChromaDB.

    Args:
        question (str): The question to retrieve relevant documents for.

    Returns:
        List[str]: A list of document IDs of the most relevant documents.
    """

    # Generate the query embedding using OpenAI
    try:
        query_embedding = embed_text(text=question, model=embedding_model_id)
    except Exception as e:
        logging.error(f"Error generating query embedding: {e}")
        return []

    # Initialize the ChromaDB client
    client = chromadb.PersistentClient(path=vector_folder_path)

    collections = client.list_collections()
    logging.info(f"Available collections: {collections}")

    collection = client.get_collection(pages_collection_name)

    # Perform a similarity search in the collection
    similar_items = collection.query(
        query_embeddings=[query_embedding],  # Now passing the actual list of embeddings
        n_results=document_count
    )

    # Extract and return the document IDs from the results
    if 'ids' in similar_items:
        document_ids = [id for sublist in similar_items['ids'] for id in sublist]
    else:
        logging.warning("No 'ids' key found in similar_items, no documents retrieved.")
        document_ids = []

    return document_ids


def vectorize_document_and_store_in_db(page_id, db_session):
    """
    Vectorize a document and store it in the database.
    :param db_session: SQLAlchemy database session.
    :param page_id: The ID of the page to vectorize.
    :return: None
    """
    page_manager = PageManager(db_session)
    page = page_manager.find_page(page_id)
    if not page:
        logging.error(f"Page content for page ID {page_id} could not be retrieved.")
        return

    page_content = page_manager.format_page_for_llm(page)
    embedding, error_message = generate_document_embedding(page_id, page_content)
    if embedding:
        if len(embedding) > 0:
            # Store the embedding in the database
            page_manager.add_or_update_embed_vector(page_id, embedding)
            logging.info(f"Embedding for page ID {page_id} stored in the database.")
        else:
            logging.error(f"Embedding for page ID {page_id} is empty.")
    else:
        logging.error(f"Embedding for page ID {page_id} could not be generated. {error_message}")
