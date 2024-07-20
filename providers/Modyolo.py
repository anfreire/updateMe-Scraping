from lib.selenium import Selenium, WebDriverWait, By, EC
from time import sleep
from GLOBAL import GLOBAL

class Base(Selenium):
    def __init__(self, link: str):
        super().__init__()
        self.link = link

    def __call__(self) -> str | None:
        link = self.getLink()
        return self.downloadFile(link) if link else None

    def getLink(self, el: bool = False) -> str:
        self.get(self.link)
        try:
            if self.current_url != self.link:
                GLOBAL.Log(f"Redirected to {self.current_url}")
                self.get(self.link)
        except:
            pass
        wait = WebDriverWait(self, 10)
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        return el.get_attribute("href") if el else None


class Modyolo(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://modyolo.com/download/{tag}/1")


class Liteapks(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://liteapks.com/download/{tag}/1")
    
    def __call__(self) -> str | None:
        self.get(self.link)
        wait = WebDriverWait(self, 10)
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        if not el or not el.get_attribute("href"):
            return None
        fun = lambda: self.clickJS(el)
        return self.monitorDownloads(fun) 
