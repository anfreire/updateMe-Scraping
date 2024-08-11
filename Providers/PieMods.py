from LIB.Selenium import Selenium, WebDriverWait, By, EC

class PieMods(Selenium):
    def __init__(self, tag: str):
        super().__init__()
        self.link = f"https://piemods.com/download/{tag}/"

    def __call__(self) -> str | None:
        self.get(self.link)
        wait = WebDriverWait(self, 10)
        href = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']")))
        return self.monitor_downloads(lambda: self.get(href.get_attribute("href")))
