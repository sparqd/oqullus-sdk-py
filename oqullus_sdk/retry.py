from __future__ import annotations

import requests
from tenacity import retry_if_exception, stop_after_attempt, wait_exponential


def _is_retryable_http_error(exc: requests.HTTPError) -> bool:
    if exc.response is None:
        return False
    status = exc.response.status_code
    return status == 429 or 500 <= status < 600


def is_retryable_exception(exc: BaseException) -> bool:
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(exc, requests.HTTPError):
        return _is_retryable_http_error(exc)
    return False


retry_policy = retry_if_exception(is_retryable_exception)
stop_policy = stop_after_attempt(3)
wait_policy = wait_exponential(multiplier=0.5, min=0.5, max=4)
