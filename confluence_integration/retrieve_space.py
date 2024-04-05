# ./confluence_integration/retrieve_space.py
# Used as part of loading documentation from confluence
import os
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence
from credentials import confluence_credentials
from database.page_manager import mark_page_as_processed
from persistqueue import Queue
from configuration import persist_page_processing_queue_path
from confluence_integration.confluence_client import ConfluenceClient
import logging


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


def choose_space():
    """
    Prompt the user to choose a Confluence space from a list of available spaces.

    Args:
    confluence_client (ConfluenceClient): The Confluence client object.

    Returns:
    str: The key of the chosen Confluence space.
    """
    confluence_client = ConfluenceClient()
    spaces = confluence_client.retrieve_space_list()
    for i, space in enumerate(spaces):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces[choice]['key'], spaces[choice]['name']


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


def check_date_filter(update_date, space_page_ids):
    """
    Filter pages based on their last updated date.

    Args:
    update_date (datetime): The threshold date for filtering. Pages updated after this date will be included.
    space_page_ids (list): A list of page IDs to be filtered.

    Returns:
    list: A list of page IDs that were last updated on or after the specified update_date.
    """
    updated_pages = []
    for page_id in space_page_ids:
        try:
            page_history = confluence.history(page_id)  # directly use page_id
        except Exception as e:
            logging.error(f"Error retrieving history for page ID {page_id}: {e}")
            continue
        last_updated = datetime.strptime(page_history['lastUpdated']['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if last_updated >= update_date:
            updated_pages.append(page_id)  # append the page_id to the list
    return updated_pages


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


def process_page(page_id, space_key, page_content_map):
    """
    Process a page and store its data in files and a database.
    :param page_id:
    :param space_key:
    :param page_content_map:
    :return: page_data
    """
    current_time = datetime.now()
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,version')
    except Exception as e:
        logging.error(f"Error retrieving page with ID {page_id}: {e}")
        return None
    if page:
        print(f"Processing page with ID {page_id}...")
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

        # Store data for database
        page_content_map[page_id] = page_data
        print(f"Page with ID {page_id} processed and written database.")

        # Mark the page as processed
        mark_page_as_processed(page_id)
        return page_data
    else:
        logging.error(f"Error processing page with ID {page_id}: Page not found.")
        return None


def get_space_content(space_key, update_date=None):
    """
    Retrieve content from a specified Confluence space and process it.

    This function allows the user to choose a Confluence space, retrieves all relevant page and comment data,
    formats it, and stores it both in files and a database.

    Args:
    update_date (datetime, optional): If provided, only pages updated after this date will be retrieved. Default is None.

    Returns:
    list: A list of IDs of all pages that were processed.
    """

    space_page_ids = get_space_page_ids(space_key)
    space_page_ids = set(space_page_ids)

    if update_date is not None:
        space_page_ids = check_date_filter(update_date, space_page_ids)

    # Setting up the persist-queue
    queue_path = os.path.join(persist_page_processing_queue_path, space_key)
    page_queue = Queue(queue_path)
    # make all page ids a set to eliminate duplicates
    for page_id in space_page_ids:
        page_queue.put(page_id)

    print(f"Enqueued {len(space_page_ids)} pages for processing.")
    print(f"Pages queued {space_page_ids}")
    return space_key