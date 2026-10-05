"""Document submission: outcome rules, persistence and misuse of the endpoint."""
from __future__ import annotations

import pytest

from idcheck_qa.api.base_client import APIError
from tests.support.documents import (
    DOCUMENT_SCENARIOS,
    INVALID_DOCUMENT,
    SPECIMEN_CNI_FRONT,
    VALID_DOCUMENT,
    Reason,
    Status,
)

pytestmark = pytest.mark.api


@pytest.mark.smoke
@pytest.mark.parametrize("scenario", DOCUMENT_SCENARIOS, ids=str)
def test_submission_decides_outcome(api_client, pending_session, scenario):
    result = api_client.submit_document(pending_session.session_id, scenario.file)

    assert result.session_id == pending_session.session_id
    assert result.status == scenario.expected_status
    assert result.reason == scenario.expected_reason


@pytest.mark.parametrize("scenario", DOCUMENT_SCENARIOS, ids=str)
def test_outcome_is_persisted_and_readable_via_status(api_client, pending_session, scenario):
    submitted = api_client.submit_document(pending_session.session_id, scenario.file)

    assert api_client.get_status(pending_session.session_id) == submitted


def test_submission_only_affects_its_own_session(api_client):
    verified = api_client.create_session()
    untouched = api_client.create_session()

    api_client.submit_document(verified.session_id, VALID_DOCUMENT.file)

    assert api_client.get_status(untouched.session_id).status == Status.PENDING


@pytest.mark.parametrize(
    "filename, expected_status",
    [
        ("INVALID_ID.JPG", Status.REJECTED),
        ("scan-invalid.png", Status.REJECTED),
        ("passport_front.jpg", Status.VERIFIED),
        ("id.pdf", Status.VERIFIED),
    ],
)
def test_outcome_rule_variants(api_client, pending_session, make_document, filename, expected_status):
    """The mock's decision rule ("invalid" in the filename, case-insensitive)."""
    result = api_client.submit_document(pending_session.session_id, make_document(filename))

    assert result.status == expected_status


def test_real_image_is_still_judged_by_filename(api_client, pending_session, make_document):
    """Same specimen bytes, "invalid" filename: documents that the mock never
    inspects image content (a real backend must decide on content)."""
    document = make_document("cni_invalid.jpg", SPECIMEN_CNI_FRONT.file.read_bytes())

    result = api_client.submit_document(pending_session.session_id, document)

    assert result.status == Status.REJECTED
    assert result.reason == Reason.DOCUMENT_UNREADABLE


# --------------------------------------------------------------------------
# Negative / out-of-order calls
# --------------------------------------------------------------------------
@pytest.mark.negative
def test_submit_to_unknown_session_returns_404(api_client):
    with pytest.raises(APIError) as exc_info:
        api_client.submit_document("000000000000", VALID_DOCUMENT.file)

    assert exc_info.value.status_code == 404
    assert exc_info.value.payload == {"error": "session_not_found"}


@pytest.mark.negative
@pytest.mark.known_defect
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: a submission without any document is VERIFIED; expected a 4xx "
    "or at least a non-VERIFIED status",
)
def test_submission_without_document_is_not_verified(api_client, pending_session):
    response = api_client.post(api_client.document_path(pending_session.session_id))

    assert response.json()["status"] != Status.VERIFIED


@pytest.mark.negative
@pytest.mark.known_defect
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: an empty (0-byte) file is VERIFIED; the content is never inspected",
)
def test_empty_document_is_not_verified(api_client, pending_session, make_document):
    result = api_client.submit_document(pending_session.session_id, make_document("id.jpg", b""))

    assert result.status != Status.VERIFIED


@pytest.mark.negative
@pytest.mark.known_defect
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: a final decision can be overwritten by re-submitting; a REJECTED "
    "session must not become VERIFIED (fraud vector)",
)
def test_rejected_session_cannot_be_overturned_by_resubmission(api_client, pending_session):
    api_client.submit_document(pending_session.session_id, INVALID_DOCUMENT.file)

    try:
        api_client.submit_document(pending_session.session_id, VALID_DOCUMENT.file)
    except APIError:
        pass  # refusing the second submission is an acceptable behaviour

    status = api_client.get_status(pending_session.session_id)
    assert status.status == Status.REJECTED
    assert status.reason == Reason.DOCUMENT_UNREADABLE


@pytest.mark.negative
def test_document_endpoint_rejects_get(api_client, pending_session):
    with pytest.raises(APIError) as exc_info:
        api_client.get(api_client.document_path(pending_session.session_id))

    assert exc_info.value.status_code == 405
