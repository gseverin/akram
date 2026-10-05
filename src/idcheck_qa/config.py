"""Centralized runtime configuration.

All values come from environment variables so no environment-specific
detail (URL, timeouts, browser choice) is hard-coded in test code. See
`.env.example` for the full list of supported keys.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("IDCHECK_BASE_URL", "http://127.0.0.1:5005")
    api_timeout: float = float(os.getenv("IDCHECK_API_TIMEOUT", "10"))
    browser: str = os.getenv("IDCHECK_BROWSER", "chrome")
    headless: bool = _bool(os.getenv("IDCHECK_HEADLESS"), True)
    ui_wait_timeout: float = float(os.getenv("IDCHECK_UI_WAIT_TIMEOUT", "10"))
    # When true the suite boots mock_server in-process on `base_url`; set to
    # false to point the same tests at an already-running/remote environment.
    start_mock_server: bool = _bool(os.getenv("IDCHECK_START_MOCK"), True)


settings = Settings()
