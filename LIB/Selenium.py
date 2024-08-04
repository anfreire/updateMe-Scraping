from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
from typing import List
import time

os.environ["WDM_LOG"] = "0"


class Selenium(WebDriver):
    def __init__(self) -> None:
        self.clean_old_session()
        super().__init__(
            service=Service(executable_path="/usr/bin/chromedriver"),
            options=self.get_options(),
        )

    def clean_old_session(self) -> None:
        os.system("pkill -f chromium")
        os.system("rm -rf /home/anfreire/.config/chromium/Singleton*")

    def get_extension_folder(self) -> str:
        folder = r"/home/anfreire/.config/chromium/Profile 1/Extensions"
        available_folder = os.listdir(folder)
        available_sub_folder = os.listdir(os.path.join(folder, available_folder[0]))
        return os.path.join(folder, available_folder[0], available_sub_folder[0])

    def get_options(self) -> Options:
        extension_folder = self.get_extension_folder()
        options = Options()
        options.enable_downloads = True
        options.add_argument(f"--load-extension={extension_folder}")
        options.add_argument("--enable-managed-downloads")
        options.add_argument(
            f"user-data-dir={os.path.expanduser('~')}/.config/chromium"
        )
        options.add_argument(f"--profile-directory=Profile 1")
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

    def click_js(self, element: WebElement) -> None:
        self.execute_script("arguments[0].click();", element)

    def list_downloadable_files(self, file_extension: str = ".apk") -> List[str]:
        return [
            a.get_attribute("href")
            for a in self.find_elements(By.TAG_NAME, "a")
            if a.get_attribute("href")
            and a.get_attribute("href").endswith(file_extension)
        ]

    def monitor_downloads(self, fun: callable, timeout: int = 150) -> str:
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        downloaded_files = os.listdir(downloads_dir)
        fun()
        tries = 0
        while tries < timeout:
            diff = [
                file
                for file in list(set(os.listdir(downloads_dir)) - set(downloaded_files))
                if file.endswith(".apk")
            ]
            if diff:
                break
            time.sleep(1)
            tries += 1
        if len(diff) == 0:
            raise Exception(f"Timeout reached, file not downloaded")
        return os.path.join(downloads_dir, diff[0])

    def download_file(self, download_link: str, timeout: int = 150) -> str:
        fun = lambda: self.get(download_link)
        return self.monitor_downloads(fun, timeout)
