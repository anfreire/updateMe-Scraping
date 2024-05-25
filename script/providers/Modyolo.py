from lib.selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from time import sleep
import subprocess


class Base(Selenium):
    def __init__(self, link: str):
        super().__init__(True)
        self.link = link

    def getLink(self) -> str:
        self.get(self.link)

        def condition():
            try:
                return self.find_element(By.CSS_SELECTOR, "a[href$='.apk']")
            except NoSuchElementException as e:
                print(e)
                return False

        try:
            element = self.getWait(timeout=15).until(condition, 12).get_attribute("href")
        except UnexpectedAlertPresentException as e:
            print(e)
            sleep(1)
            element = self.getWait(timeout=15).until(condition, 12).get_attribute("href")
        return element


class Modyolo(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://modyolo.com/download/{tag}/1")
        self.tag = tag

    def getLink_alt(self) -> str:
        os.system(
            f"flatpak run com.google.Chrome https://modyolo.com/download/{self.tag}/1 --start-maximized 2> /dev/null > /dev/null &"
        )
        sleep(10)
        sleep(1)
        return subprocess.check_output(["xclip", "-o"]).decode()

    @property
    def origin(self) -> str:
        return f"https://liteapks.com/download/{self.tag}/1"


class Liteapks(Base):
    def __init__(self, tag: str):
        super().__init__(f"https://liteapks.com/download/{tag}/1")
        self.tag = tag

    @property
    def origin(self) -> str:
        return f"https://liteapks.com/download/{self.tag}/1"


class Moddroid(Base):
    def __init__(self, rest: str):
        self.link = f"https://moddroid.com/{rest}"
        super().__init__(self.link)

    @property
    def origin(self) -> str:
        return self.link