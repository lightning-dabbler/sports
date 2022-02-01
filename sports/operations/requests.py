import backoff
import requests
import urllib3.exceptions
from loguru import logger

MAX_WAIT_SECONDS = 100
MAX_TRIES = 9


def fatal_code(e):
    logger.debug(f"Backoff: Error involving 'make_request' found! {e.__class__}", error=e, **e.__dict__)
    errors = [
        isinstance(e, requests.exceptions.ConnectionError),
        isinstance(e, urllib3.exceptions.MaxRetryError),
        isinstance(e, urllib3.exceptions.ProtocolError),
        isinstance(e, OSError),
    ]
    giveup = not any(errors)
    message = "Giving up..." if giveup else "Due for retry..."
    logger.debug(message, giveup=giveup)
    return giveup


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.ProtocolError, OSError),
    max_tries=MAX_TRIES,
    giveup=fatal_code,
    max_value=MAX_WAIT_SECONDS,
    base=6,  # --> https://github.com/litl/backoff/blob/master/backoff/_wait_gen.py
)
def make_request(url, method="GET", **kwargs):
    logger.debug("Making request to: {url}", url=url, method=method, **kwargs)
    return requests.request(method, url, **kwargs)
