from LIB.Selenium import Selenium, By, WebDriverWait, EC, WebElement
from GLOBAL import GLOBAL
from typing import TypedDict
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

SearchResultDict = TypedDict(
    "SEARCH_RESULT", {"title": str, "link": str, "author": str, "date": datetime}
)


class Mobilism(Selenium):
    def __init__(self):
        super().__init__()
        self.login()

    def __call__(
        self,
        app_name: str,
        search: str,
        user: str,
        include_words_search: list[str] = [],
        exclude_words_search: list[str] = [],
        include_words_filename: list[str] = [],
        exclude_words_filename: list[str] = [],
    ) -> str | None:
        posts = self.search(search, user)
        parsed_posts = self.parse_search(
            posts, include_words_search, exclude_words_search
        )
        elements = self.get_elements(parsed_posts[0]["link"])
        links = self.get_links(elements)
        filenames = list(set([self.extract_filename(link) for link in links]))
        if not len(filenames):
            return None
        filenames = [x for x in filenames if x]
        filtered = []
        if len(include_words_filename):
            for filename in filenames:
                if all(
                    1
                    for word in include_words_filename
                    if word.lower() in filename.lower()
                ):
                    filtered.append(filename)
        else:
            filtered = filenames
        filtered_2 = []
        if len(exclude_words_filename):
            for filename in filtered:
                if not any(
                    1
                    for word in exclude_words_filename
                    if word.lower() in filename.lower()
                ):
                    filtered_2.append(filename)
        else:
            filtered_2 = filtered
        if not len(filtered_2):
            return None
        GLOBAL.Index[app_name]["providers"][user]["source"] = parsed_posts[0]["link"]
        link = self.make_link(filtered_2[0])
        return self.monitor_downloads(
            lambda: self.execute_script(
                f"""var iframe = document.createElement('iframe');
                iframe.src = '{link}';
                document.body.appendChild(iframe);"""
            )
        )

    def login(self):
        try:
            self.get("https://forum.mobilism.me/ucp.php?mode=login")
            wait = WebDriverWait(self, 4)
            username = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
            )
            username.send_keys(GLOBAL.Config["Mobilism"]["USER"])
            password = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
            )
            password.send_keys(GLOBAL.Config["Mobilism"]["PASSWORD"])
            submit = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#load"))
            )
            submit.click()
        except Exception as e:
            pass

    def search(
        self,
        keywords: str,
        author: str | None = None,
    ) -> list[WebElement]:
        self.get("https://forum.mobilism.me/search.php")
        wait = WebDriverWait(self, 4)
        search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#keywords"))
        )
        search.send_keys(keywords)
        if author:
            author_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#author"))
            )
            author_input.send_keys(author)
        wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "button[data-original-title='Post time']",
                )
            )
        ).click()
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//a[@tabindex='0']/span[contains(text(), 'Topic time')]",
                )
            )
        ).find_element(By.XPATH, "ancestor::a").click()
        wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "button[name='submit']",
                )
            )
        ).click()
        return wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "td.expand.footable-first-column")
            )
        )

    def parse_search(
        self,
        tds: list[WebElement],
        include_words: list[str] = [],
        exclude_words: list[str] = [],
    ) -> list[SearchResultDict]:
        results = []
        for td in tds:
            aTitle: WebElement = td.find_element(By.CSS_SELECTOR, "a.topictitle")
            title = aTitle.text
            if len(include_words) and any(
                1 for word in include_words if word.lower() not in title.lower()
            ):
                continue
            if len(exclude_words) and any(
                1 for word in exclude_words if word.lower() in title.lower()
            ):
                continue
            link = aTitle.get_attribute("href")
            aAuthor: WebElement = td.find_element(
                By.CSS_SELECTOR, "a[href*='memberlist.php?']"
            )
            author = aAuthor.text
            date = td.find_element(By.TAG_NAME, "small").text
            if "Yesterday" in date:
                date = date.replace(
                    "Yesterday", (datetime.now() - timedelta(1)).strftime("%b %d, %Y")
                )
            elif "Today" in date:
                date = date.replace("Today", datetime.now().strftime("%b %d, %Y"))
            else:
                date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date)
            date = datetime.strptime(date, "%b %d, %Y, %I:%M %p")
            results.append(
                {"title": title, "link": link, "author": author, "date": date}
            )
        results.sort(key=lambda x: x["date"], reverse=True)
        return results

    def get_elements(self, link: str) -> list[WebElement]:
        self.get(link)
        wait = WebDriverWait(self, 4)
        try:
            download_title_span = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "span[style='text-decoration: underline']")
                )
            )
        except Exception:
            return None
        for span in download_title_span:
            if span.text == "Download Instructions:":
                download_title_span = span
                break
        return download_title_span.find_elements(By.XPATH, "following-sibling::*")

    def parse_elements_v1(
        self, next_elements: list[WebElement]
    ) -> dict[str, dict[str, str]]:
        results = {}
        title, curr_subtitle, links = None, None, {}
        for element in next_elements:
            match element.tag_name:
                case "span":
                    is_bold = False
                    try:
                        if "font-weight: bold" in element.get_attribute("style"):
                            is_bold = True
                        child = element.find_element(By.CSS_SELECTOR, "span")
                        if "font-weight: bold" in child.get_attribute("style"):
                            is_bold = True
                        if is_bold:
                            if title:
                                results[title] = links
                                title, curr_subtitle, links = None, None, {}
                            title = child.text
                    except Exception:
                        curr_subtitle = element.text
                        pass
                case "a":
                    if curr_subtitle and "postlink" in element.get_attribute("class"):
                        links[curr_subtitle] = element.get_attribute("href")
                        curr_subtitle = None
        if title:
            results[title] = links
        return results

    def parse_elements_v2(
        self, next_elements: list[WebElement]
    ) -> dict[str, list[str]]:
        results = {}
        title, links = None, []
        for element in next_elements:
            match element.tag_name:
                case "span":
                    if element.text and "mirrors" in element.text.lower():
                        continue
                    else:
                        if title:
                            results[title] = links
                            title, links = None, []
                        title = element.text
                case "a":
                    if "postlink" in element.get_attribute(
                        "class"
                    ) and element.get_attribute("href"):
                        links.append(element.get_attribute("href"))
        if title:
            results[title] = links
        return results

    def get_links(self, next_elements: list[WebElement]) -> list[str]:
        return [
            a.get_attribute("href")
            for a in next_elements
            if a.tag_name == "a"
            and a.get_attribute("href")
            and "postlink" in a.get_attribute("class")
        ]

    def extract_filename(self, link: str) -> str:
        if "frdl" in link:
            if link.endswith(".html"):
                link = link[:-5]
            if link.endswith(".apk"):
                return link.split("/")[-1].replace(" ", "_")
        res = requests.get(link)
        soup = BeautifulSoup(res.text, "html.parser")
        match link[8:].split("/")[0]:
            case "devuploads.com":
                return soup.select_one("input[name='title'][type='hidden'][value]").get(
                    "value"
                )
            case "uploady.io":
                text = [
                    h1.text for h1 in soup.find_all("h1") if h1.text.endswith(".apk")
                ][0]
                if text.startswith("Download file: "):
                    text = text[15:]
                return text.replace(" ", "_")
            case "mega4upload.com":
                return (
                    [tag.text for tag in soup.find_all() if tag.text.endswith(".apk")][
                        0
                    ]
                    .split("/")[-1]
                    .replace(" ", "_")
                )
            case "katfile.com":
                return [
                    text.strip()
                    for text in [
                        tag.text for tag in soup.find_all() if ".apk" in tag.text
                    ][0].split("\n")
                    if text.strip().endswith(".apk")
                ][0].replace(" ", "_")
            case "www.up-4ever.net":
                return (
                    [tag.text for tag in soup.find_all() if tag.text.endswith(".apk")][
                        0
                    ]
                    .replace("Download File ", "")
                    .replace(" ", "_")
                )
            case "uploadrar.com":
                self.get(link)
                wait = WebDriverWait(self, 10)
                # button = .find_element(By.CSS_SELECTOR, "button[name='method_free']")
                button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[name='method_free']"))
                )
                button.click()
                span = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div > div > div.blockpage > div.desc > span:nth-child(1)"))
                )
                return span.text

    def make_link(self, filename) -> str:
        return GLOBAL.Config["Mobilism"]["BASE_URL"] + filename
