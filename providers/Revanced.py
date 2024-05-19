from scrappers.Selenium import Selenium, By
from providers.Github import Github
from typing import List
import re
import time


class Revanced(Selenium):
    def __init__(self, suffix: str):
        self.link = f"https://revanced.net/{suffix}"
        super().__init__()

    def getLink(self) -> str:
        self.openLink(self.link)
        tbodies = self.getElements(By.TAG_NAME, "tbody")
        for tbodie in tbodies:
            row = tbodie.find_element(By.TAG_NAME, "tr")
            link = None
            for cell in row.find_elements(By.TAG_NAME, "td"):
                try:
                    link = cell.find_element(By.TAG_NAME, "a").get_attribute("href")
                    if link:
                        break
                except:
                    pass
            if link and link.endswith(".apk"):
                break
            else:
                link = None
        return link if link else self.alt()

    def get_bigger_version(self, versions: List[str]) -> str:
        pattern = re.compile(r"_v([\d.]+)_cli")
        versions_to_version = {
            version: pattern.search(version).group(1) for version in versions
        }
        return max(versions_to_version, key=versions_to_version.get)

    def get_link_gh(self, includes: List[str], excludes: List[str]) -> tuple:
        gh = Github("revancedapps", "revanced.net")
        versions = gh.getVersions()
        count = 0
        link = None
        while link is None and count < len(versions):
            links = gh.getLinks(versions[count], includes, excludes)
            if len(links) > 0:
                link = self.get_bigger_version(links)
            count += 1
        return (link, gh.origin)
