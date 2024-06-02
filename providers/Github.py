from typing import List
import re
from lib.selenium import Selenium, By, WebDriverWait, EC


class Github(Selenium):
    def __init__(self, user: str, repo: str):
        self.user = user
        self.repo = repo

    @property
    def prefix(self):
        return f"https://github.com/{self.user}/{self.repo}"

    def getVersions(self) -> List[str]:
        self.get(f"{self.prefix}/releases")
        divs = self.find_elements(by=By.TAG_NAME, value="div")
        versions = list()
        for div in divs:
            if div.find_element(By.XPATH, ".//svg[@aria-label='Tag']") and div.find_element(By.TAG_NAME, "span"):
                try:
                    text = div.find_element(By.TAG_NAME, "span").text
                    text = re.sub(r"\s+", "", text)
                    if (
                        text == self.user
                        or text == self.repo
                        or text is None
                        or len(text) == 0
                        or text in versions
                    ):
                        continue
                    versions.append(text)
                except:
                    continue
        return versions
    
    @property
    def origin(self) -> str:
        return f"{self.prefix}/releases"

    def getLinks(
        self, version: str, include: List[str] = [], exclude: List[str] = []
    ) -> List[str]:
        self.get(f"{self.prefix}/releases/expanded_assets/{version}")
        lis = self.find_elements(By.TAG_NAME, "li")
        links = []
        for li in lis:
            div = li.find_element(By.TAG_NAME, "div")
            if div.find_element(By.XPATH, ".//svg") and div.find_element(By.TAG_NAME, "a"):
                href = div.find_element(By.TAG_NAME, "a").get_attribute("href")
                if (
                    href
                    and len(href) != 0
                    and all(term in href for term in include)
                    and all(term not in href for term in exclude)
                ):
                    link = (
                        href
                        if href.startswith("https://")
                        else "https://github.com/" + href
                    )
                    if link not in links:
                        links.append(link)
        return links
