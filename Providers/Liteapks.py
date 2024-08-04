from LIB.Selenium import Selenium, WebDriverWait, By, EC, WebElement
from GLOBAL import GLOBAL


class Liteapks(Selenium):
    def __init__(self, tag: str):
        super().__init__()
        self.link = f"https://liteapks.com/download/{tag}/1"

    def __call__(self) -> str | None:
        self.get(self.link)
        wait = WebDriverWait(self, 10)
        el: WebElement = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        if not el or not el.get_attribute("href"):
            return None
        fun = lambda: self.click_js(el)
        return self.monitor_downloads(fun)
