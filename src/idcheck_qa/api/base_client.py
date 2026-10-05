"""Thin, reusable HTTP client wrapper.

Kept separate from the domain client (`IdentityVerificationClient`) so
transport concerns (persistent session, timeouts, error mapping) never
leak into business/test logic, and any future API in the project can
reuse it as-is.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised for any non-2xx response, carrying enough context for assertions."""

    def __init__(self, method: str, url: str, status_code: int, payload: Any):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"{method} {url} -> HTTP {status_code}: {payload!r}")


class BaseAPIClient:
    """Generic JSON/multipart REST client built on a persistent `requests.Session`."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout)
        logger.debug("%s %s", method, url)
        response = self.session.request(method, url, **kwargs)
        if not response.ok:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise APIError(method, url, response.status_code, payload)
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def close(self) -> None:
        self.session.close()
