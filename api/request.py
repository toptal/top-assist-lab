import requests
import logging


def post_request(url, payload, headers=None, data_type=None):
    """
    Post a request to a given URL.
    :param data_type: Type of payload data.
    :param url: The URL to post to.
    :param payload: The payload to send.
    :param headers: The headers to send.
    :return: The response from the server.
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"INFO: {data_type} request submitted to {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"ERROR: An HTTP error with {data_type} request occurred: {e}")
    except Exception as e:
        logging.error(f"ERROR: An error with {data_type} request occurred: {e}")
