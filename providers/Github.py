from typing import List
import re
from lib.selenium import Selenium, By, WebDriverWait, EC


class Github(Selenium):
    def __init__(self, user: str, repo: str):
        self.user = user
        self.repo = repo
        super().__init__()

    @property
    def prefix(self):
        return f"https://github.com/{self.user}/{self.repo}"

    def __call__(self, include: List[str] = [], exclude: List[str] = []) -> str | None:
        tags = self.getTags()
        for tag in tags:
            link = self.getLinks(tag, include, exclude)
            if link:
                return self.downloadFile(link)
        return None

    def getTags(self) -> List[str]:
        self.get(f"{self.prefix}/tags")
        hrefs = self.find_elements(By.TAG_NAME, "a")
        prefix = f"{self.prefix}/releases/tag/"
        tags = []
        for href in hrefs:
            if href.get_attribute("href") and href.get_attribute("href").startswith(
                prefix
            ):
                tag = href.get_attribute("href").replace(prefix, "")
                if tag not in tags:
                    tags.append(tag)
        return tags

    def getLinks(
        self, tag: str, include: List[str] = [], exclude: List[str] = []
    ) -> str | None:
        self.get(f"{self.prefix}/releases/expanded_assets/{tag}")
        files = self.listDownloadableFiles()
        prefix = f"{self.prefix}/releases/download/{tag}/"
        for file in files:
            file = file.replace(prefix, "")
            if (
                len(file) != 0
                and all(term in file for term in include)
                and all(term not in file for term in exclude)
            ):
                return f"{prefix}{file}"
        return None
