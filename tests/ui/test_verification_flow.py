"""End-to-end verification flow: API for setup/oracle, browser for the user journey."""
from __future__ import annotations

import pytest

from tests.support.documents import DOCUMENT_SCENARIOS, Status

pytestmark = pytest.mark.e2e


@pytest.mark.smoke
@pytest.mark.parametrize("scenario", DOCUMENT_SCENARIOS, ids=str)
def test_capture_flow_reaches_expected_outcome(
    api_client, pending_session, upload_page, result_page, scenario
):
    # Arrange: the client app creates the session (API, no UI needed)
    session_id = pending_session.session_id

    # Act: the end user captures and submits through the web page
    upload_page.open(session_id)
    assert upload_page.displayed_session_id() == session_id
    upload_page.capture_document(scenario.file).submit()

    # Assert: same outcome on the result page and in the API
    assert result_page.wait_for_status(scenario.expected_status) == scenario.expected_status
    api_status = api_client.get_status(session_id)
    assert api_status.status == scenario.expected_status
    assert api_status.reason == scenario.expected_reason


@pytest.mark.parametrize("scenario", DOCUMENT_SCENARIOS, ids=str)
def test_result_page_reflects_api_decision(api_client, pending_session, result_page, scenario):
    """State is set through the API; only the rendering is checked in the browser."""
    api_client.submit_document(pending_session.session_id, scenario.file)

    result_page.open(pending_session.session_id)

    assert result_page.current_status() == scenario.expected_status


def test_result_page_of_session_not_yet_submitted_shows_pending(pending_session, result_page):
    result_page.open(pending_session.session_id)

    assert result_page.current_status() == Status.PENDING


@pytest.mark.negative
def test_result_page_of_unknown_session_shows_unknown(result_page):
    result_page.open("000000000000")

    assert result_page.current_status() == Status.UNKNOWN
