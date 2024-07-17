import time
from lib.selenium import Selenium, By
from time import sleep
from typing import TypedDict
import datetime

downloadInfo = TypedDict(
    "downloadInfo",
    {
        "date": datetime.date,
        "size": str,
    },
)


class ApkDone(Selenium):
    def __init__(self, tag: str):
        self.link = f"https://apkdone.com/{tag}/download"
        super().__init__()

    def __call__(self) -> str | None:
        link = self.getLink()
        return self.downloadFile(link) if link else None

    def getLink(self):
        self.get(self.link)
        aTags = self.find_elements(By.TAG_NAME, "a")
        links = {}
        for a in aTags:
            try:
                if a.get_attribute("href") and a.get_attribute("href").endswith(
                    "download"
                ):
                    parent = a.find_element(By.XPATH, "../..")
                    info = parent.find_element(By.TAG_NAME, "div")
                    spans = info.find_elements(By.CSS_SELECTOR, "span.chip-text")
                    date = None
                    size = None
                    for span in spans:
                        if span.text.count("-") == 2:
                            date = datetime.datetime.strptime(
                                span.text, "%Y-%m-%d"
                            ).date()
                        if any(
                            [
                                size
                                for size in ["kb", "mb", "gb"]
                                if size in span.text.lower()
                            ]
                        ):
                            extension = span.text.split(" ")[1].lower()
                            sizeFloat = float(span.text.split(" ")[0])
                            match extension:
                                case "kb":
                                    size = sizeFloat
                                case "mb":
                                    size = sizeFloat * 1024
                                case "gb":
                                    size = sizeFloat * 1024 * 1024
                    links[a.get_attribute("href")] = downloadInfo(date=date, size=size)
            except:
                pass
        if len(links) == 0:
            return None
        elif len(links) == 1:
            return list(links.keys())[0]
        mostRecent = None
        for link in links:
            if mostRecent is None:
                mostRecent = link
            elif links[link]["date"] > links[mostRecent]["date"]:
                mostRecent = link
            elif links[link]["date"] == links[mostRecent]["date"]:
                if links[link]["size"] > links[mostRecent]["size"]:
                    mostRecent = link
        return mostRecent
