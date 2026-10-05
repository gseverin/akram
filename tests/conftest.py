"""Suite-wide fixtures: configuration, app-under-test lifecycle, API client.

Layering mirrors the starter code:
    transport (BaseAPIClient) -> domain (IdentityVerificationClient,
    Page Objects) -> tests. Tests only talk to the domain layer, plus the
    transport layer for deliberately malformed requests.
"""
from __future__ import annotations

import threading
import uuid
from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests
from dotenv import load_dotenv

# Must run before `idcheck_qa.config` is imported: Settings reads the
# environment at import time. `.env` never overrides real env vars, so CI
# can inject values without touching files.
load_dotenv()

from idcheck_qa.api.identity_api_client import IdentityVerificationClient  # noqa: E402
from idcheck_qa.config import Settings, settings as default_settings  # noqa: E402



@pytest.fixture(scope="session")
def settings() -> Settings:
    return default_settings


# --------------------------------------------------------------------------
# App under test
# --------------------------------------------------------------------------
class _MockServer:
    """Runs mock_server.app in a background thread for the whole session."""

    def __init__(self, base_url: str):
        from werkzeug.serving import make_server

        from mock_server.app import app

        parsed = urlparse(base_url)
        self._server = make_server(parsed.hostname, parsed.port or 80, app, threaded=True)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self) -> "_MockServer":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._server.shutdown()
        self._thread.join(timeout=5)


@pytest.fixture(scope="session")
def app_under_test(settings: Settings):
    """Make sure the service is reachable at `settings.base_url`.

    Boots the mock in-process unless IDCHECK_START_MOCK=false, in which
    case the suite targets whatever is already running at that URL.
    """
    if settings.start_mock_server:
        try:
            server = _MockServer(settings.base_url)
        except (OSError, SystemExit):  # werkzeug turns "address in use" into sys.exit(1)
            pytest.exit(
                f"Cannot bind {settings.base_url}. Stop the server already "
                "running there or set IDCHECK_START_MOCK=false to reuse it.",
                returncode=3,
            )
        with server:
            _wait_until_healthy(settings)
            yield settings.base_url
    else:
        _wait_until_healthy(settings)
        yield settings.base_url


def _wait_until_healthy(settings: Settings, attempts: int = 50) -> None:
    for _ in range(attempts):
        try:
            if requests.get(settings.base_url, timeout=1).ok:
                return
        except requests.ConnectionError:
            pass
        threading.Event().wait(0.1)
    pytest.exit(f"Service not reachable at {settings.base_url}", returncode=3)


@pytest.fixture(autouse=True)
def _isolated_backend_state(request, settings: Settings):
    """Clear in-memory sessions after each test when we own the mock.

    Tests never rely on this for correctness (each one creates its own
    session), it only keeps the mock's memory from growing.
    """
    yield
    if settings.start_mock_server and "app_under_test" in request.fixturenames:
        from mock_server.app import reset_state

        reset_state()


# --------------------------------------------------------------------------
# API layer
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api_client(app_under_test: str, settings: Settings):
    client = IdentityVerificationClient(app_under_test, timeout=settings.api_timeout)
    yield client
    client.close()


@pytest.fixture
def applicant_ref() -> str:
    """Synthetic, unique, non-identifying applicant reference."""
    return f"qa-auto-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def pending_session(api_client: IdentityVerificationClient, applicant_ref: str):
    """A fresh session in PENDING state, created through the API."""
    return api_client.create_session(applicant_ref=applicant_ref)


@pytest.fixture
def make_document(tmp_path):
    """Factory for synthetic upload files with a chosen filename.

    The mock decides the outcome from the filename, so variants (case,
    extension, prefixes) are generated on the fly instead of committing a
    file per case.
    """

    def _make(filename: str, content: bytes = b"synthetic-test-document") -> Path:
        path = tmp_path / filename
        path.write_bytes(content)
        return path

    return _make
