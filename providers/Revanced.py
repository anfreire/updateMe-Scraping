from lib.selenium import Selenium, By


class Revanced(Selenium):
    def __init__(self, suffix: str):
        self.link = f"https://revanced.net/{suffix}"
        super().__init__()

    def __call__(self) -> str | None:
        link = self.getLink()
        return self.downloadFile(link) if link else None

    def getLink(self) -> str:
        self.get(self.link)
        tbodies = self.find_elements(By.TAG_NAME, "tbody")
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
        return link
