from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence
import logging

from credentials import confluence_credentials


# Initialize Confluence API
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
)


def get_space_page_ids(space_key):
    """
    Retrieves all page IDs in a given space, including child pages.

    Args:
    space_key (str): The key of the Confluence space.

    Returns:
    list: A list of all page IDs in the space.
    """
    page_ids = []
    start = 0
    limit = 50
    while True:
        try:
            chunk = confluence.get_all_pages_from_space(space_key, start=start, limit=limit)
            start += limit
        except Exception as e:
            logging.error(f"Error fetching pages (space_key={space_key} start={start} limit={limit}): {e}")
            break

        page_ids.extend([page["id"] for page in chunk])
        if len(chunk) < limit:
            break

    return page_ids


def check_date_filter(update_date, page_ids):
    """
    Filter pages based on their last updated date.

    Args:
    update_date (datetime): The threshold date for filtering. Pages updated after this date will be included.
    page_ids (list): A list of page IDs to be filtered.

    Returns:
    list: A list of page IDs that were last updated on or after the specified update_date.
    """
    updated_pages = []
    for page_id in page_ids:
        try:
            page_history = confluence.history(page_id)  # directly use page_id
        except Exception as e:
            logging.error(f"Error retrieving history for page ID {page_id}: {e}")
            continue
        last_updated = datetime.strptime(page_history['lastUpdated']['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if last_updated >= update_date:
            updated_pages.append(page_id)  # append the page_id to the list
    return updated_pages


def strip_html_tags(content):
    """
    Remove HTML tags from a string.

    Args:
    content (str): The string with HTML content.

    Returns:
    str: The string with HTML tags removed.
    """
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()


def get_page_comments_content(page_id):
    """
    Retrieve and format the content of all comments on a Confluence page.

    Args:
    page_id (str): The ID of the Confluence page.

    Returns:
    str: A string containing the content of all comments on the page.
    """
    result = []
    start = 0
    limit = 25
    while True:
        try:
            chunk = confluence.get_page_comments(page_id, depth='all', start=start, limit=limit, expand='body.storage')['results']
        except Exception as e:
            logging.error(f"Error fetching page comments (page_id={page_id}) start={start} limit={limit}): {e}")
            break

        for comment in chunk:
            content = comment['body']['storage']['value']
            content = strip_html_tags(content)
            result.append(content)

        start += limit
        if len(chunk) < limit:
            break

    return '\n'.join(result)


def retrieve_page(page_id, space_key):
    """
    Retrieves page data
    :param page_id:
    :param space_key:
    :return: page_data
    """
    current_time = datetime.now()
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,version')
    except Exception as e:
        logging.error(f"Error retrieving page with ID {page_id}: {e}")
        return None

    if not page:
        logging.error(f"Error processing page with ID {page_id}: Page not found.")
        return None

    logging.info(f"Processing page with ID {page_id}...")
    page_title = strip_html_tags(page['title'])
    page_author = page['history']['createdBy']['displayName']
    created_date = page['history']['createdDate']
    last_updated = page['version']['when']
    page_content = strip_html_tags(page.get('body', {}).get('storage', {}).get('value', ''))
    page_comments_content = get_page_comments_content(page_id)

    page_data = {
        'spaceKey': space_key,
        'pageId': page_id,
        'title': page_title,
        'author': page_author,
        'createdDate': created_date,
        'lastUpdated': last_updated,
        'content': page_content,
        'comments': page_comments_content,
        'datePulledFromConfluence': current_time
    }

    logging.info(f"Page with ID {page_id} retrieved.")
    return page_data


def retrieve_pages(space_key, page_ids):
    pages = []
    def worker(page_id):
        logging.info(f"Processing page with ID {page_id}...")
        page_data = retrieve_page(page_id, space_key)
        if page_data:
            pages.append(page_data)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, page_id) for page_id in page_ids]
        for future in as_completed(futures):
            page_data = future.result()
            if page_data:
                pages.append(page_data)

    return pages


def retrieve_space(space_key, update_date=None):
    logging.info(f"Starting retrieval for space key: {space_key}")

    page_ids = get_space_page_ids(space_key)
    page_ids = list(set(page_ids))
    if update_date:
        page_ids = check_date_filter(update_date, page_ids)
    logging.info(f'Discovered {len(page_ids)} pages for retrieval.')

    pages = retrieve_pages(space_key, page_ids)
    logging.info(f"Finished retrieval for space key: {space_key}")

    return pages
