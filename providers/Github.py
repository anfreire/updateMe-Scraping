from scrappers.UrlLib import UrlLib
from typing import List
import re


class Github(UrlLib):
    def __init__(self, user: str, repo: str):
        self.user = user
        self.repo = repo

    @property
    def prefix(self):
        return f"https://github.com/{self.user}/{self.repo}"

    def getVersions(self) -> List[str]:
        self.getPage(f"{self.prefix}/releases")
        divs = self.getTags("div")
        versions = list()
        for div in divs:
            if div.find("svg", attrs={"aria-label": "Tag"}) and div.find("span"):
                try:
                    text = div.find("span").text
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
        self.getPage(f"{self.prefix}/releases/expanded_assets/{version}")
        lis = self.getTags("li")
        links = []
        for li in lis:
            div = li.find("div")
            if div and div.find("svg") and div.find("a"):
                href = div.find("a").get("href")
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
