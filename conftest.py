import allure
import pytest
from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.chrome.service import Service as ChromeService

from src.utils.settings_reader import SettingsReader

qa_auto_config = {}  # Config()

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="qa", help="Env to run test against (qa, prod)")
    parser.addoption("--browser", action="store", default="chrome",
                     help="Browser to run: chrome, chrome-selenium-standalone, chrome-docker")
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")

def pytest_configure(config):
    settings = SettingsReader()
    base_url_ui = settings.get_base_ui_url(env=config.getoption("--env"))
    qa_auto_config.update({"base_url_ui": base_url_ui})

@allure.title("Create config")
@pytest.fixture(scope="session")
def auto_config() -> dict:
    return qa_auto_config

@pytest.fixture(scope="session")
def driver(request):
    # setup
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    # Works with image "selenium/standalone-chrome:latest"
    if browser.lower() == "chrome-selenium-standalone":
        options = ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        driver = Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=options
        )
    elif browser.lower() == "chrome-docker":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")  # For debugging
        options.binary_location = "/opt/chrome/chrome-linux64/chrome"
        chrome_service = ChromeService(executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver")
        driver = Chrome(service=chrome_service, options=options)
    elif browser.lower() == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        driver = Chrome(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    driver.maximize_window()
    yield driver
    # teardown
    driver.quit()
