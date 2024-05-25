from lib.selenium import Selenium, By
from selenium.common.exceptions import NoSuchElementException

class ApkDone(Selenium):
	def __init__(self, tag: str):
		self.link = f"https://apkdone.com/{tag}/download"
		super().__init__()

	def getLink(self) -> str:
		self.get(self.link)

		def condition():
			try:
				return self.find_element(By.CSS_SELECTOR, "a[href$='download'][data-filename$='.apk']")
			except NoSuchElementException as e:
				print(e)
				return False

		return self.getWait().until(condition).get_attribute("href")