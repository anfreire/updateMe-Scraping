from selenium.webdriver import ChromeOptions, ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from GLOBAL import GLOBAL
import os
from webdriver_manager.chrome import ChromeDriverManager
import time


class Selenium(WebDriver):
    def __init__(self) -> None:
        self.cleanOldSession()
        super().__init__(
            service=ChromeService(ChromeDriverManager().install()),
            options=self.getOptions(),
        )

    def cleanOldSession(self) -> None:
        os.system("pkill -f chromium")
        os.system("rm -rf /home/anfreire/.config/chromium/Singleton*")

    def getExtensionFolder(self) -> str:
        folder = r"/home/anfreire/.config/chromium/Profile 1/Extensions"
        availableFolder = os.listdir(folder)
        availableSubFolder = os.listdir(os.path.join(folder, availableFolder[0]))
        return os.path.join(folder, availableFolder[0], availableSubFolder[0])

    def getOptions(self) -> ChromeOptions:
        extensionFolder = self.getExtensionFolder()
        options = ChromeOptions()
        options.enable_downloads = True
        options.add_argument(f"--load-extension={extensionFolder}")
        options.add_argument("--enable-managed-downloads")
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": os.path.join(
                    os.path.expanduser("~"), "Downloads"
                ),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )
        return options

    def clickJS(self, element: WebElement) -> None:
        self.execute_script("arguments[0].click();", element)

    def listDownloadableFiles(self, fileExtension: str = '.apk') -> dict:
        return [a.get_attribute("href") for a in self.find_elements(By.TAG_NAME, "a") if a.get_attribute("href") and a.get_attribute("href").endswith(fileExtension)]
    
    def downloadFile(self, download_link: str, timeout: int = 25) -> str:
        downloadsDir = os.path.join(os.path.expanduser("~"), "Downloads")
        for file in os.listdir(downloadsDir):
            if file.endswith(".apk"):
                os.remove(os.path.join(downloadsDir, file))
        downloadedFiles = os.listdir(downloadsDir)
        self.get(download_link)
        tries = 0
        while tries < timeout:
            diff = [file for file in list(set(os.listdir(downloadsDir)) - set(downloadedFiles)) if file.endswith(".apk")]
            if diff:
                break
            time.sleep(1)
            tries += 1
        if len(diff) == 0:
            raise Exception(f"Timeout reached, file from {download_link} not downloaded")
        return os.path.join(downloadsDir, diff[0])