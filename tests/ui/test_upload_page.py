"""Capture page behaviour beyond the happy path."""
from __future__ import annotations

from urllib.parse import quote

import pytest
from selenium.webdriver.common.by import By

from tests.support.documents import Status

pytestmark = pytest.mark.negative


@pytest.mark.known_defect
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: 'Submit capture' with no file uploads the string 'undefined' "
    "and the session is VERIFIED; the UI should block the submission",
)
def test_submit_without_capture_does_not_verify(
    api_client, pending_session, upload_page, result_page
):
    upload_page.open(pending_session.session_id).submit()
    result_page.wait_until_loaded()  # redirect happens only once the upload has completed

    assert api_client.get_status(pending_session.session_id).status != Status.VERIFIED


@pytest.mark.known_defect
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: the capture page renders for any session id instead of an error",
)
def test_capture_page_for_unknown_session_shows_an_error(upload_page):
    upload_page.open("000000000000")

    assert upload_page.driver.find_elements(By.ID, "document-input") == []


@pytest.mark.security
def test_session_id_in_url_is_html_escaped(upload_page):
    """A crafted link must not inject markup/script into the capture page."""
    payload = '<img id="injected" src="x" onerror="document.title=\'pwned\'">'

    upload_page.open(quote(payload, safe=""))

    assert upload_page.displayed_session_id() == payload
    assert upload_page.driver.find_elements(By.ID, "injected") == []
    assert upload_page.driver.title != "pwned"
