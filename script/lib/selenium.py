import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class Selenium(webdriver.Chrome):
    def __init__(self) -> None:
        self.exterminate()
        self.service = Service("/usr/bin/chromedriver")
        self.options = Options()
        # self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": "/home/anfreire/Downloads",
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        super().__init__(service=self.service, options=self.options)

    def exterminate(self) -> None:
        os.system("pkill -f chromium")
        os.system("rm -rf /home/anfreire/.config/chromium/Singleton*")

    def execJS(self, *args) -> None:
        self.execute_script(*args)

    def clickJS(self, element: WebElement) -> None:
        self.execJS("arguments[0].click();", element)

    def getWait(self, root: WebElement = None, timeout: int = 10) -> WebDriverWait:
        return WebDriverWait(self if root is None else root, timeout)
