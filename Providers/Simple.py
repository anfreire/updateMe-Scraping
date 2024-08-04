from LIB.Selenium import Selenium, By, WebDriverWait, EC
from typing import List


class Simple(Selenium):
    def __init__(self):
        super().__init__()

    def __call__(
        self,
        link: str,
        include: List[str] = [],
        exclude: List[str] = [],
    ) -> str | None:
        link = self.getLink(link, include, exclude)
        return self.download_file(link) if link else None

    def getLink(
        self,
        link: str,
        include: List[str] = [],
        exclude: List[str] = [],
    ) -> str:
        self.get(link)
        wait = WebDriverWait(self, 10)
        hrefs = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        for href in hrefs:
            href = href.get_attribute("href")
            if len(include) and not all([i.lower() in href.lower() for i in include]):
                continue
            if len(exclude) and any([e.lower() in href.lower() for e in exclude]):
                continue
            return href
