from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver
from typing import List
import os


class Selenium:
    def __init__(self, uc: bool = False) -> None:
        self.extension = self.getExtensionFolder()
        os.system("pkill -f chromium")
        os.system("rm -rf /home/anfreire/.config/chromium/Singleton*")
        self.driver = self.getDriver(uc)

    def getExtensionFolder(self) -> None:
        """Gets the folder of the extension"""
        folder = r"/home/anfreire/.config/chromium/Profile 1/Extensions"
        available_dirs0 = os.listdir(folder)
        available_dirs1 = os.listdir(f"{folder}/{available_dirs0[0]}")
        return rf"{folder}/{available_dirs0[0]}/{available_dirs1[0]}"

    def getDriver(self, uc: bool = False) -> webdriver.Chrome:
        """Gets a Chrome driver

        Args:
            uc (bool, optional): Whether to use undetected_chromedriver. Defaults to False.

        Returns:
            webdriver.Chrome: The Chrome driver
        """
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service)
        return driver

    def openLink(self, link: str) -> None:
        """Opens a link in the browser

        Args:
            link (str): The link to be opened
        """
        self.driver.get(link)

    def getElements(self, by: By, value: str) -> List[WebElement]:
        """Returns a list of elements with the given tag

        Args:
            by (By): The method to find the elements
            value (str): The value to find the elements

        Returns:
            List[WebElement]: The elements found
        """

        return self.driver.find_elements(by, value)

    def exec(self, *args) -> None:
        """Executes JavaScript

        Args:
            *args: The JavaScript to be executed
        """
        self.driver.execute_script(*args)

    def clickJS(self, element: WebElement) -> None:
        """Clicks an element using JavaScript

        Args:
            element (WebElement): The element to be clicked
        """
        self.exec("arguments[0].click();", element)

    def waitCustom(self, condition: callable, timeout: int = 10) -> WebElement:
        """Waits for a custom condition to be met"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(condition)

    def waitToFind(self, by: By, value: str, timeout: int = 10) -> WebElement:
        """Waits for an element to be present and returns it

        Args:
            by (By): The method to find the element
            value (str): The value to find the element
            timeout (int, optional): The time to wait for the element to be present. Defaults to 10.

        Raises:
            TimeoutException: If the element is not present after the timeout

        Returns:
            WebElement: The element found
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def waitToClick(self, element: WebElement, timeout: int = 10) -> None:
        """Waits for an element to be clickable and then clicks it

        Args:
            element (WebElement): The element to be clicked
            timeout (int, optional): The time to wait for the element to be clickable. Defaults to 10.

        Raises:
            TimeoutException: If the element is not clickable after the timeout
        """
        clickableElement = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(element)
        )
        clickableElement.click()
