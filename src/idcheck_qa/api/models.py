"""Typed response models, decoupled from raw dict payloads.

Dataclasses (instead of asserting on raw JSON in every test) keep test
code readable and give a single place to adapt if the API contract
changes shape.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VerificationSession:
    session_id: str
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> "VerificationSession":
        return cls(session_id=data["session_id"], status=data["status"])


@dataclass(frozen=True)
class VerificationStatus:
    session_id: str
    status: str
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "VerificationStatus":
        return cls(
            session_id=data["session_id"],
            status=data["status"],
            reason=data.get("reason"),
        )
