"""Base Page Object: shared navigation/wait helpers for every page.

Every concrete page inherits from this so common behaviour (explicit
waits, safe click/type/read) is written once; locators and page-specific
flows live only in the subclasses.
"""
from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, wait_timeout: float = 10.0):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, wait_timeout)

    def _open(self, path: str) -> None:
        self.driver.get(f"{self.base_url}/{path.lstrip('/')}")

    def _find(self, locator) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def _click(self, locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _text_of(self, locator) -> str:
        return self._find(locator).text
