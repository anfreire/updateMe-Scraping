from lib.selenium import Selenium, By, WebDriverWait, EC
from selenium.common.exceptions import NoSuchElementException

class ApkDone(Selenium):
	def __init__(self, tag: str):
		self.link = f"https://apkdone.com/{tag}/download"
		super().__init__()

	def fun(self) -> str:
		self.get(self.link)

		def condition(driver):
			try:
				return driver.find_element(By.CSS_SELECTOR, "a[href$='download'][data-filename$='.apk']")
			except NoSuchElementException:
				return False

		wait = WebDriverWait(self, 10)
		el = wait.until(condition)
		href = el.get_attribute("href")
		return self.downloadFile(href)