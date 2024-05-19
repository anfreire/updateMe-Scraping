from scrappers.Selenium import Selenium
from selenium.webdriver.common.by import By


class Aero(Selenium):

	def remove_adblock(self):
		h2 = self.driver.find_elements(By.XPATH, "//h2")
		found = None
		for h in h2:
			if h.text == "Looks like your ad blocker is on  🥺":
				found = h
				break
		if not found:
			return
		parent = found.find_element(By.XPATH, "../../..")
		if parent:
			self.execute_script("arguments[0].remove();", parent)

	def open(self, link):
		self.openLink(link)
		self.remove_adblock()

	def get_href_by_text(self, text: str) -> str | None:
		elememts = self.driver.find_elements(By.TAG_NAME, "a")
		for el in elememts:
			if el.text == text and el.get_attribute("href"):
				return el.get_attribute("href")

	def click_span(self, class_attr: str):
		spans = self.driver.find_elements(By.TAG_NAME, "span")
		for span in spans:
			if span.get_attribute("class") == class_attr:
				self.clickJS(span)
				break
	
	def get_href_by_ending_link(self, text: str) -> str | None:
		elememts = self.driver.find_elements(By.XPATH, "//a[@href]")
		for el in elememts:
			if el.get_attribute("href").endswith(text):
				return el.get_attribute("href")
