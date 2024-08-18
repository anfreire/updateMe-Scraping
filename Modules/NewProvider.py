from GLOBAL import GLOBAL, Provider, App
from Modules.Writter import LinkSuffixProvider
from Modules.Searcher import Searcher
from typing import Dict, Callable, List, Tuple, TypeAlias, Generator
from LIB.CLI import CLI
import pickle
import os
import blessed
from dataclasses import dataclass

PROVIDER = "MODZOCO"


@dataclass
class Result:
    info: any
    source: str


class NewProvider:
    def __init__(self):
        self.ignored_apps: List[str] = []

    def __call__(self) -> None:
        if os.path.exists(GLOBAL.Paths.Files.NewProviderBackup) and CLI.confirm(
            title="Restore previous session?",
            message="Do you want to restore the previous session?",
        ):
            self.__read_config()
        for app in self.iter_apps():
            try:
                os.system("killall chromium > /dev/null 2>&1")
                searcher = Searcher(PROVIDER)
                searcher.search(app)
                results = searcher.get_results()
                for title, href in results.items():
                    if app.lower() in title.lower():
                        origin, tag = searcher.get_origin_and_tag(href)
                        provider = LinkSuffixProvider(origin, PROVIDER, PROVIDER, tag)
                        self.ignored_apps.append(app)
                        GLOBAL.Index[app].providers[PROVIDER] = {
                            "source": origin,
                            "version": "",
                            "packageName": "",
                            "download": "",
                            "safe": True,
                            "sha256": "",
                        }
                        GLOBAL.Index.write()
                        GLOBAL.Apps[app].providers[PROVIDER] = provider.build_provider()
                        GLOBAL.Apps.write()
                        print(f"Added {app} to the index")
                        self.__save_config()
                        break
            except Exception as e:
                GLOBAL.Log(f"Error while searching {app}: {e}", exception=True)
                continue

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
        term = blessed.Terminal()
        for app in reversed(list(GLOBAL.Index.keys())):
            if app in self.ignored_apps:
                continue
            providers = GLOBAL.Index[app].providers.keys()
            if PROVIDER in providers:
                GLOBAL.Log(
                    f"Skipping {app} because it has already the provider {PROVIDER}"
                )
                continue
            with term.cbreak():
                print(f"\nShould I search {app}? (y/n) ", end="", flush=True)
                val = term.inkey()
                if val == "y":
                    yield app
                else:
                    self.ignored_apps.append(app)
                    self.__save_config()


def main():
    NewProvider()()
