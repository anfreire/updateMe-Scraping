import requests
import json
from LIB.Selenium import Selenium, WebDriverWait, EC, By
from typing import Literal
from GLOBAL import GLOBAL

RAW_DOURCE_INDEX = "https://gist.github.com/xC3FFF0E/5268182b9bc89832a9cfbe2eb0568c3c/raw/xManager.json"


KEYWORDS = {
    "stock": "Stock_Patched",
    "amoled": "Amoled_Patched",
    "lite": "Lite_Patched",
}


class xManager(Selenium):

    def __init__(self):
        super().__init__()
        self.data = None

    def __call__(self, type: Literal["stock", "amoled", "lite"]):
        try:
            response = requests.get(RAW_DOURCE_INDEX)
            self.data = response.json()
            link = self.__get_data(type)
            self.get(link)
            wait = WebDriverWait(self, 10)
            el = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#download-pane > div.buttons > div.download-button.generic-button.green"
                    )
                )
            )
            return self.monitor_downloads(lambda :self.click_js(el))
        except Exception as e:
            GLOBAL.Log(f"Error: {e}", level="ERROR", exception=GLOBAL.Args.debug)
            return None

    def __get_data(self, type: Literal["stock", "amoled", "lite"]):
        return self.__get_link(self.data[KEYWORDS[type]][0])

    def __get_link(self, data: dict[str, str]):
        for value in data.values():
            if value.startswith("https://fileport.io/"):
                return value
        return None
