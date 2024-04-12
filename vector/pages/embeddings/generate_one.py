import logging

from configuration import embedding_model_id
from database.page_manager import PageManager
from open_ai.embedding.embed_manager import embed_text


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_one_embedding_to_database(page_id):
    """
    Vectorize a document and store it in the database.
    :param page_id: The ID of the page to vectorize.
    :return: None
    """
    page = PageManager().find_page(page_id)
    if not page:
        logging.error(f"Page content for page ID {page_id} could not be retrieved.")
        return

    page_content = PageManager().format_page_for_llm(page)
    page_content = page_content[:8190] # Ensure the content does not exceed the maximum token limit
    try:
        # embed_text now returns a serialized JSON string of the embedding vector
        embedding = embed_text(text=page_content, model=embedding_model_id)
    except Exception as e:
        error_message = f"Error generating embedding for page ID {page_id}: {e}\n"
        logging.error(error_message)
        return

    if len(embedding) > 0:
        # Store the embedding in the database
        PageManager().add_or_update_embed_vector(page_id, embedding)
        logging.info(f"Embedding for page ID {page_id} stored in the database.")
    else:
        logging.error(f"Embedding for page ID {page_id} is empty.")
