"""Isolates WebDriver construction so tests/pages never touch Selenium
`Options`/`Service` directly. Adding a second browser later means editing
one method, not every test.
"""
from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class DriverFactory:
    """Factory for browser sessions."""

    @staticmethod
    def create(browser: str = "chrome", headless: bool = True) -> webdriver.Remote:
        if browser.lower() != "chrome":
            raise ValueError(f"Unsupported browser: {browser}")

        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(0)  # explicit waits only -- see BasePage
        return driver
