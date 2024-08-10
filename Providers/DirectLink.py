from LIB.Selenium import Selenium, By, WebDriverWait, EC
from typing import List


class DirectLink(Selenium):
    def __init__(self):
        super().__init__()

    def __call__(
        self,
        link: str,
    ) -> str | None:
        return self.download_file(link)
