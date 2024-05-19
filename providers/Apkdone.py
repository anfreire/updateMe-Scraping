from scrappers.Selenium import Selenium, By
from selenium.common.exceptions import NoSuchElementException

class ApkDone(Selenium):
	def __init__(self, tag: str):
		self.link = f"https://apkdone.com/{tag}/download"
		super().__init__()

	def getLink(self) -> str:
		self.openLink(self.link)

		def condition(driver):
			try:
				return driver.find_element(By.CSS_SELECTOR, "a[href$='download'][data-filename$='.apk']")
			except NoSuchElementException:
				return False

		return self.waitCustom(condition).get_attribute("href")