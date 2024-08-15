from LIB.Selenium import WebElement, WebDriver, Selenium, WebDriverWait, EC, By
from GLOBAL import GLOBAL
from typing import Dict, Callable, List, Tuple, TypeAlias, Generator
from LIB.CLI import CLI
import pickle
from Providers.PieMods import PieMods
import os
from dataclasses import dataclass


@dataclass
class Result:
    info: any
    source: str


SearchFun: TypeAlias = Callable[[Selenium, str], Dict[str, Result]]
DownloadFun: TypeAlias = Callable[[Selenium, Result], Callable[[], None]]


class NewProvider:
    def __init__(self, provider: str, search: SearchFun, download: DownloadFun):
        self.provider = provider
        self.search: SearchFun = search
        self.download: DownloadFun = download
        self.ignored_apps: List[str] = []

    def __call__(self) -> None:
        if os.path.exists(GLOBAL.Paths.Files.NewProviderBackup) and CLI.confirm(
            title="Restore previous session?",
            message="Do you want to restore the previous session?",
        ):
            self.__read_config()
        for app in self.iter_apps():
            try:
                self.driver = Selenium()
                results: Dict[str, Result] = self.search(self.driver, app)
                self.driver.quit()
            except Exception as e:
                GLOBAL.Log(f"Error while searching {app}: {e}")
                continue
            results = {
                key: value
                for key, value in results.items()
                if app.lower() in key.lower()
            }
            for result, info in results.items():
                try:
                    result = self.download(self.driver, info)
                except Exception as e:
                    GLOBAL.Log(f"Error while downloading {result}: {e}")
                    continue
                if CLI.confirm(
                    title="Add app to the index?",
                    message=f"Do you want to add the app {app} to the index?\nThis is the link: {info.source}",
                ):
                    self.ignored_apps.append(app)
                    provider = {
                        "source": info.source,
                        "version": "",
                        "packageName": "",
                        "download": "",
                        "safe": True,
                        "sha256": "",
                    }
                    GLOBAL.Index[app].providers[self.provider] = provider
                    GLOBAL.Index.write()

    def __read_config(self):
        with open(GLOBAL.Paths.Files.NewProviderBackup, "rb") as file:
            self.ignored_apps = pickle.load(file)

    def __save_config(self):
        with open(GLOBAL.Paths.Files.NewProviderBackup, "wb") as file:
            pickle.dump(self.ignored_apps, file)

    def __remove_config(self):
        if os.path.exists(GLOBAL.Paths.Files.NewProviderBackup):
            os.remove(GLOBAL.Paths.Files.NewProviderBackup)

    def iter_apps(self) -> Generator[str, None, None]:
        for app in GLOBAL.Index.keys():
            if app in self.ignored_apps:
                continue
            providers = GLOBAL.Index[app].providers.keys()
            if self.provider in providers:
                GLOBAL.Log(
                    f"Skipping {app} because it has already the provider {self.provider}"
                )
                continue
            if CLI.confirm(
                title="Add app to the index?",
                message=f"Do you want to add the app {app} to the index?",
            ):
                yield app
            else:
                self.ignored_apps.append(app)
                self.__save_config()


def main():
    provider = "PieMods"

    def search(driver: Selenium, query: str) -> Dict[str, str]:
        driver.get("https://piemods.com/")
        wait = WebDriverWait(driver, 10)
        driver.click_js(
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#header > div:nth-child(2) > div > div > div:nth-child(3) > div > button",
                    )
                )
            )
        )
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#search-modal > div.ct-panel-content > form > input")
            )
        ).send_keys(query)
        driver.click_js(
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#search-modal > div.ct-panel-content > form > div.ct-search-form-controls > button",
                    )
                )
            )
        )
        a_tags = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a[href^='https://piemods.com/']")
            )
        )
        build_info = lambda a: Result(
            [tag for tag in a.get_attribute("href").split("/") if len(tag)][-1],
            a.get_attribute("href"),
        )
        return {a.text: build_info(a) for a in a_tags}

    def download(driver: Selenium, result: Result) -> Callable[[], None]:
        return PieMods(result.info)()

    NewProvider(provider, search, download)()
