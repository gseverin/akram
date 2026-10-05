"""Page Object for the verification result screen.

TODO (candidate): implement the methods below using the locator already
defined and the `_text_of` helper inherited from `BasePage` (see
`base_page.py`). The page served at `GET /result/{session_id}` (see
`mock_server/app.py`) exposes a span #verification-status holding the
current status text (e.g. "VERIFIED", "REJECTED").
"""
from __future__ import annotations

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By

from .base_page import BasePage


class ResultPage(BasePage):
    _STATUS_LABEL = (By.ID, "verification-status")

    def open(self, session_id: str) -> "ResultPage":
        """Navigate straight to the result screen of a session."""
        self._open(f"/result/{session_id}")
        return self

    def wait_until_loaded(self) -> "ResultPage":
        """Wait for the result screen to render, whatever the status."""
        self._find(self._STATUS_LABEL)
        return self

    def wait_for_status(self, expected_status: str) -> str:
        """Wait until the displayed status equals `expected_status`, then return it."""
        last_seen: list[str] = []

        def _status_matches(driver) -> bool:
            # The label may not exist yet (still on the capture page) or be
            # replaced mid-read during the redirect: both mean "not yet".
            try:
                elements = driver.find_elements(*self._STATUS_LABEL)
                if not elements:
                    return False
                text = elements[0].text.strip()
            except StaleElementReferenceException:
                return False
            last_seen[:] = [text]
            return text == expected_status

        try:
            self.wait.until(_status_matches)
        except TimeoutException as exc:
            seen = last_seen[0] if last_seen else "<status label never rendered>"
            raise TimeoutException(
                f"Expected status {expected_status!r}, last displayed: {seen!r} "
                f"(url={self.driver.current_url})"
            ) from exc
        return expected_status

    def current_status(self) -> str:
        """Return the currently displayed status without waiting."""
        return self.driver.find_element(*self._STATUS_LABEL).text.strip()
