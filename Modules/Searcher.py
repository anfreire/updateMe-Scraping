from LIB.Selenium import Selenium, By, WebDriverWait, EC
from typing import Literal


PROVIDERS_KEYS = Literal["MODYOLO", "LITEAPKS", "APKDONE", "MODZOCO"]


URLS = {
    "MODYOLO": lambda x: f"https://modyolo.com/?s={x}",
    "LITEAPKS": lambda x: f"https://liteapks.com/?s={x}",
    "APKDONE": lambda x: f"https://apkdone.com/search/{x}",
    "MODZOCO": lambda x: f"https://modzoco.com/?s={x}",
}


TITLE_AND_HREF_SELECTORS = {
    "MODYOLO": {
        "parent": "a.archive-post[title][href]",
        "href": lambda x: x.get_attribute("href"),
        "title": lambda x: x.get_attribute("title"),
    },
    "LITEAPKS": {
        "parent": "a.archive-post[title][href]",
        "href": lambda x: x.get_attribute("href"),
        "title": lambda x: x.get_attribute("title"),
    },
    "APKDONE": {
        "parent": "a[title][href]",
        "href": lambda x: x.get_attribute("href"),
        "title": lambda x: x.get_attribute("title"),
    },
    "MODZOCO": {
        "parent": "a.archive-post[title][href]",
        "href": lambda x: x.get_attribute("href"),
        "title": lambda x: x.get_attribute("title"),
    },
}


class Searcher(Selenium):
    def __init__(self, provider: PROVIDERS_KEYS):
        self.provider = provider
        super().__init__()

    def search(self, search: str):
        self.get(URLS[self.provider](search.replace(" ", "+")))

    def get_results(self) -> dict[str, str]:
        wait = WebDriverWait(self, 10)
        return {
            TITLE_AND_HREF_SELECTORS[self.provider]["title"](
                parent
            ): TITLE_AND_HREF_SELECTORS[self.provider]["href"](parent)
            for parent in wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, TITLE_AND_HREF_SELECTORS[self.provider]["parent"])
                )
            )
        }

    def get_origin_and_tag(self, href: str) -> tuple[str, str]:
        if self.provider == "APKDONE":
            return href, href.split("/")[3]
        self.get(href)
        wait = WebDriverWait(self, 10)
        a = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.btn.btn-primary[href]")
            )
        )
        for i in a:
            if "download" in i.get_attribute("href"):
                return href, i.get_attribute("href").split("/")[-1]

    @staticmethod
    def solve_captcha(provider: PROVIDERS_KEYS):
        import os
        import random

        os.system("killall chromium > /dev/null 2>&1")
        os.system(
            f"python3 /home/anfreire/Documents/UpdateMe/Scrapping/Modules/Captcha.py '{URLS[provider](str(random.random()))}'"
        )
