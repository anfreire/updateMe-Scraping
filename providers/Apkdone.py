from lib.selenium import Selenium, By, WebDriverWait, EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep

class ApkDone(Selenium):
	def __init__(self, tag: str):
		self.link = f"https://apkdone.com/{tag}/download"
		super().__init__()

	def __call__(self) -> str | None:
		link = self.getLink()
		return self.downloadFile(link) if link else None
	
	def getLink(self) -> str | None:
		self.get(self.link)

		def condition(driver: Selenium):
			try:
				return driver.find_element(By.CSS_SELECTOR, "a[href$='download'][data-filename$='.apk']")
			except NoSuchElementException:
				return False
		try:
			return WebDriverWait(self, 10).until(condition).get_attribute("href")
		except:
			sleep(1)
			try:
				return WebDriverWait(self, 15).until(condition).get_attribute("href")
			except:
				pass
		return None