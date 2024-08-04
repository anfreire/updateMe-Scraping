from LIB.Selenium import Selenium, WebDriverWait, By, EC, WebElement
from GLOBAL import GLOBAL


class Modyolo(Selenium):
    def __init__(self, tag: str):
        super().__init__()
        self.tag = f"https://modyolo.com/download/{tag}/1"

    def __call__(self) -> str | None:
        self.get(self.tag)
        wait = WebDriverWait(self, 20)
        el: WebElement = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        if not el or not el.get_attribute("href"):
            return None
        return self.download_file(el.get_attribute("href"))
