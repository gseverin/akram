"""Session lifecycle and response contract of /api/sessions."""
from __future__ import annotations

import re

import pytest

from idcheck_qa.api.base_client import APIError
from tests.support.documents import Status

pytestmark = pytest.mark.api

SESSION_ID_PATTERN = re.compile(r"^[0-9a-f]{12}$")


@pytest.mark.smoke
def test_create_session_returns_pending_session(pending_session):
    assert SESSION_ID_PATTERN.match(pending_session.session_id)
    assert pending_session.status == Status.PENDING


def test_create_session_responds_201_with_json(api_client):
    response = api_client.post(api_client.SESSIONS_PATH, json={"applicant_ref": "qa-auto"})

    assert response.status_code == 201
    assert response.headers["Content-Type"].startswith("application/json")
    assert set(response.json()) == {"session_id", "status"}


def test_new_session_status_is_pending_without_reason(api_client, pending_session):
    status = api_client.get_status(pending_session.session_id)

    assert status.session_id == pending_session.session_id
    assert status.status == Status.PENDING
    assert status.reason is None


def test_status_response_shape(api_client, pending_session):
    payload = api_client.get(api_client.session_path(pending_session.session_id)).json()

    assert set(payload) == {"session_id", "status", "reason"}


def test_session_ids_are_unique(api_client):
    ids = {api_client.create_session().session_id for _ in range(20)}

    assert len(ids) == 20


@pytest.mark.negative
@pytest.mark.parametrize(
    "session_id",
    ["000000000000", "does-not-exist", "UPPERCASE123", "a" * 256],
    ids=["well-formed-unknown", "malformed", "wrong-case", "very-long"],
)
def test_get_status_of_unknown_session_returns_404(api_client, session_id):
    with pytest.raises(APIError) as exc_info:
        api_client.get_status(session_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.payload == {"error": "session_not_found"}


@pytest.mark.negative
def test_status_is_not_reachable_with_post(api_client, pending_session):
    with pytest.raises(APIError) as exc_info:
        api_client.post(api_client.session_path(pending_session.session_id))

    assert exc_info.value.status_code == 405
