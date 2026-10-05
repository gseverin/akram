"""Test data catalogue: every document scenario the suite knows about.

Scenarios are declared once here and reused by API and UI tests through
parametrization, so adding a case (new document type, new rejection
reason) is a one-line change instead of a new test.

All files are synthetic placeholders or official public SPECIMEN images
(French CNI specimen, fictitious holder "Marie Martin") -- never commit
real ID documents or anything derived from a real person, even
"anonymised" ones.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class Status:
    """Session statuses exposed by the API and the result page."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"  # result page only, for sessions the backend doesn't know


class Reason:
    DOCUMENT_UNREADABLE = "document_unreadable"


@dataclass(frozen=True)
class DocumentScenario:
    id: str
    file: Path
    expected_status: str
    expected_reason: Optional[str] = None

    def __str__(self) -> str:  # readable pytest ids
        return self.id


VALID_DOCUMENT = DocumentScenario(
    id="valid-document",
    file=FIXTURES_DIR / "valid_id.jpg",
    expected_status=Status.VERIFIED,
)
INVALID_DOCUMENT = DocumentScenario(
    id="invalid-document",
    file=FIXTURES_DIR / "invalid_id.jpg",
    expected_status=Status.REJECTED,
    expected_reason=Reason.DOCUMENT_UNREADABLE,
)

# Realistic captures: real JPEGs of an official specimen card, front and back.
SPECIMEN_CNI_FRONT = DocumentScenario(
    id="specimen-cni-front",
    file=FIXTURES_DIR / "specimen_cni_recto.jpg",
    expected_status=Status.VERIFIED,
)
SPECIMEN_CNI_BACK = DocumentScenario(
    id="specimen-cni-back",
    file=FIXTURES_DIR / "specimen_cni_verso.jpg",
    expected_status=Status.VERIFIED,
)

DOCUMENT_SCENARIOS = [VALID_DOCUMENT, INVALID_DOCUMENT, SPECIMEN_CNI_FRONT, SPECIMEN_CNI_BACK]
