"""Browser fixtures. Everything under tests/ui is marked `ui` automatically."""
from __future__ import annotations

import pytest

from idcheck_qa.config import Settings
from idcheck_qa.ui.driver_factory import DriverFactory
from idcheck_qa.ui.pages.result_page import ResultPage
from idcheck_qa.ui.pages.upload_document_page import UploadDocumentPage


def pytest_collection_modifyitems(items):
    for item in items:
        if "/tests/ui/" in str(item.path).replace("\\", "/"):
            item.add_marker(pytest.mark.ui)


@pytest.fixture(scope="session")
def driver(settings: Settings):
    """One browser for the whole run (start-up dominates UI test time)."""
    web_driver = DriverFactory.create(browser=settings.browser, headless=settings.headless)
    yield web_driver
    web_driver.quit()


@pytest.fixture
def browser(driver):
    """Per-test view of the shared browser, reset so tests stay independent."""
    yield driver
    driver.delete_all_cookies()
    driver.get("about:blank")


@pytest.fixture
def upload_page(browser, app_under_test: str, settings: Settings) -> UploadDocumentPage:
    return UploadDocumentPage(browser, app_under_test, settings.ui_wait_timeout)


@pytest.fixture
def result_page(browser, app_under_test: str, settings: Settings) -> ResultPage:
    return ResultPage(browser, app_under_test, settings.ui_wait_timeout)
