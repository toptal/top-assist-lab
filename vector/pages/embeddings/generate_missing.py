import logging
import requests
import time

from configuration import api_host, api_port
from database.page_manager import PageManager


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def submit_embedding_creation_request(page_id: str):
    endpoint_url = f'http://{api_host}:{api_port}/api/v1/embeds'
    headers = {"Content-Type": "application/json"}
    payload = {"page_id": page_id}

    try:
        response = requests.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise for HTTP errors
        logging.info(f"Embedding creation request successful for page ID {page_id}.")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred while submitting embedding creation request for page ID {page_id}: {e}")
    except Exception as e:
        logging.error(f"An error occurred while submitting embedding creation request for page ID {page_id}: {e}")


def generate_missing_embeddings_to_database(retry_limit: int = 3, wait_time: int = 5) -> None:
    for attempt in range(retry_limit):
        # Retrieve the IDs of pages that are still missing embeddings.
        page_ids = PageManager().get_page_ids_missing_embeds()
        # If there are no pages missing embeddings, exit the loop and end the process.
        if not page_ids:
            logging.info("All pages have embeddings. Process complete.")
            return

        logging.info(f"Attempt {attempt + 1} of {retry_limit}: Processing {len(page_ids)} pages missing embeddings.")
        for page_id in page_ids:
            # Submit a request to generate an embedding for each page ID.
            submit_embedding_creation_request(page_id)
            # A brief delay between requests to manage load and potentially avoid rate limiting.
            time.sleep(0.2)

        logging.info(f"Waiting for {wait_time} seconds for embeddings to be processed...")
        time.sleep(wait_time)

        # After waiting, retrieve the list of pages still missing embeddings to see if the list has decreased.
        # This retrieval is crucial to ensure that the loop only continues if there are still pages that need processing.
        if page_ids := PageManager().get_page_ids_missing_embeds():
            logging.info(f"After attempt {attempt + 1}, {len(page_ids)} pages are still missing embeds.")
        else:
            break  # Break out of the loop if there are no more pages missing embeddings.

    # After exhausting the retry limit, check if there are still pages without embeddings.
    if page_ids:
        logging.info("Some pages still lack embeddings after all attempts.")
    else:
        logging.info("All pages now have embeddings. Process complete.")
