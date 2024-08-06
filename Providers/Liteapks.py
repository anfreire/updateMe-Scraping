from LIB.Selenium import Selenium, WebDriverWait, By, EC, WebElement
from GLOBAL import GLOBAL


class Liteapks(Selenium):
    def __init__(self, tag: str):
        super().__init__()
        self.link = f"https://liteapks.com/download/{tag}"

    def __call__(self) -> str | None:
        self.get(self.link)
        wait = WebDriverWait(self, 10)
        els: list[WebElement] = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, f"a[href^='{self.link}']")
            )
        )
        found = False
        arm7_keywords = ["armv7", "armeabi", "arm7"]
        arm64_keywords = ["arm64", "armv8", "arch64"]
        for el in els:
            spans = el.find_elements(By.XPATH, ".//span")
            if any(
                span
                for span in spans
                if any(
                    [
                        keyword in span.get_attribute("innerHTML").lower()
                        for keyword in arm7_keywords
                    ]
                )
            ):
                GLOBAL.Log(f"Fuond armeabi. Skipping")
                continue
            if any(
                span
                for span in spans
                if any(
                    [
                        keyword in span.get_attribute("innerHTML").lower()
                        for keyword in arm64_keywords
                    ]
                )
            ):
                GLOBAL.Log(f"Found arm64. Downloading")
                self.get(el.get_attribute("href"))
                found = True
                break
        if not found:
            self.get(self.link + "/1")
        el: WebElement = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href$='.apk']"))
        )
        if not el or not el.get_attribute("href"):
            return None
        fun = lambda: self.click_js(el)
        return self.monitor_downloads(fun)
