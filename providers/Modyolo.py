from lib.selenium import Selenium, WebDriverWait, By, EC
from time import sleep


class Base(Selenium):
    def __init__(self, link: str):
        super().__init__()
        self.link = link

    def __call__(self) -> str | None:
        link = self.getLink()
        return self.downloadFile(link) if link else None

    def getLink(self, el: bool = False) -> str:
        self.get(self.link)

        seconds = 0
        while seconds < 15:
            try:
                el = self.find_element(By.CSS_SELECTOR, "a[href$='.apk']")
                return el.get_attribute("href")
            except:
                sleep(1)
                seconds += 1
        return None


class Modyolo(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://modyolo.com/download/{tag}/1")


class Liteapks(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://liteapks.com/download/{tag}/1")
