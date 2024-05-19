from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4.element import PageElement
from bs4.element import ResultSet


class UrlLib:
    def __init__(self) -> None:
        self.page = None

    def getPage(self, link) -> BeautifulSoup:
        rawPage = urlopen(link)
        self.page = BeautifulSoup(rawPage, "html.parser")

    def getTags(self, tag: str) -> ResultSet[PageElement]:
        return self.page.find_all(tag)
