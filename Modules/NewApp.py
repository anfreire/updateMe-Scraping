from GLOBAL import GLOBAL, IndexApp, IndexProvider, LogLevel
from Modules.Writter import (
    GithubProvider,
    LinkSuffixProvider,
    HrefFinderProvider,
    DirectLinkProvider,
    Writter,
)
from Modules.Searcher import Searcher
from LIB.CLI import CLI, StyleType
from LIB.Github import Github
from LIB.Thread import Thread
import pickle
import os
import requests
import json
import re


class NewApp:
    def __init__(self):
        super().__init__()
        self.__threads: dict[str, Thread] = {}
        self.__variables = {
            "name": None,
            "icon": None,
            "dependencies": None,
            "complements": None,
            "features": None,
            "providers": None,
        }
        self.__get_initial_data()
        self.__restore_config()

    def __get_initial_data(self):
        def get_existing_apps():
            return list(GLOBAL.Index.keys())

        def get_features():
            return list(
                {feature for app in GLOBAL.Index.values() for feature in app.features}
            )

        def get_providers():
            return list(
                {
                    provider
                    for app in GLOBAL.Index.values()
                    for provider in app.providers
                }
            )

        self.__threads = {
            "existing_apps": Thread(get_existing_apps),
            "features": Thread(get_features),
            "providers": Thread(get_providers),
        }

    def __read_config(self):
        with open(GLOBAL.Paths.Files.NewAppBackup, "rb") as file:
            self.__variables = pickle.load(file)

    def __save_config(self):
        with open(GLOBAL.Paths.Files.NewAppBackup, "wb") as file:
            pickle.dump(self.__variables, file)

    def __remove_config(self):
        if os.path.exists(GLOBAL.Paths.Files.NewAppBackup):
            os.remove(GLOBAL.Paths.Files.NewAppBackup)

    def __restore_config(self):
        if not os.path.exists(GLOBAL.Paths.Files.NewAppBackup):
            return
        if CLI.confirm(
            title="Restore previous session?",
            message="Do you want to restore the previous session?",
        ):
            self.__read_config()

    def __get_name(self) -> None:
        value = ""
        self.existing_apps = self.__threads["existing_apps"].result()
        while True:
            value = CLI.input("Enter the app name: ")
            if value is None:
                exit()
            value = value.strip()
            if len(value) == 0:
                CLI.message(
                    title="Invalid Name",
                    message="The name cannot be empty",
                    type=StyleType.ERROR,
                )
                continue
            if any(value == app for app in self.existing_apps):
                CLI.message(
                    title="Invalid Name",
                    message="The name already exists",
                    type=StyleType.ERROR,
                )
                continue
            self.__variables["name"] = value
            break

    def __get_icon(self) -> None:
        iconPath = os.path.join(
            GLOBAL.Paths.Directories.Icons,
            re.sub(r"[^a-zA-Z0-9_]", "", self.__variables["name"].lower()) + ".png",
        )
        while True:
            if os.path.exists(iconPath):
                if CLI.confirm(
                    title="Icon already exists",
                    message="Do you want to use it?",
                ):
                    self.__variables["icon"] = Github.push_icon(iconPath)
                    break
                else:
                    if CLI.confirm(
                        title="Remove existing icon",
                        message="Do you want to remove the existing icon?",
                    ):
                        os.remove(iconPath)
                    else:
                        continue
            icon = CLI.input("Enter the app icon url: ")
            if icon is None:
                exit()
            icon = icon.strip()
            if len(icon) == 0:
                CLI.message(
                    title="Invalid Icon",
                    message="The icon cannot be empty",
                    type=StyleType.ERROR,
                )
                continue
            response = None
            try:
                response = requests.get(icon)
            except Exception:
                pass
            if response is None or response.status_code != 200:
                CLI.message(
                    title="Invalid Icon",
                    message="The icon url is invalid",
                    type=StyleType.ERROR,
                )
                continue
            with open(iconPath, "wb") as file:
                file.write(response.content)
            self.__variables["icon"] = Github.push_icon(iconPath)
            break

    def __get_providers(self) -> None:
        self.features = self.__threads["features"].result()
        providers_autocomplete = self.__threads["providers"].result()
        self.__variables["providers"] = []
        while True:
            if CLI.confirm(
                title="Add Provider",
                message="Do you want to add a provider?",
            ):
                provider = CLI.select(
                    title="Select Provider",
                    message="Select the provider to add",
                    options=["Github", "LinkSuffix", "HrefFinder", "DirectLink"],
                )
                if provider is None:
                    exit()
                match provider:
                    case "Github":
                        user = CLI.input(
                            "Enter the Github user: ",
                            suggestions=providers_autocomplete,
                        )
                        if user is None:
                            exit()
                        repo = CLI.input("Enter the Github repo: ")
                        if repo is None:
                            exit()
                        include_words = CLI.multiline_input(
                            "Enter the include words (one per line)"
                        )
                        exclude_words = CLI.multiline_input(
                            "Enter the exclude words (one per line)"
                        )
                        self.__variables["providers"].append(
                            GithubProvider(
                                origin=f"https://github.com/{user}/{repo}",
                                provider_name="Github",
                                user=user,
                                repo=repo,
                                include_words=include_words,
                                exclude_words=exclude_words,
                            )
                        )
                    case "LinkSuffix":
                        provider = CLI.select(
                            title="Select Provider",
                            message="Select the provider to add",
                            options=["MODYOLO", "LITEAPKS", "APKDONE", "MODZOCO"],
                        )
                        tries = 0
                        while tries < 3:
                            try:
                                searcher = Searcher(provider)
                                searcher.search(self.__variables["name"])
                                results = searcher.get_results()
                                origin, suffix = searcher.get_origin_and_tag(results[self.__variables["name"]])
                            except Exception as e:
                                print(e)
                                suffix = None
                                if tries < 2:
                                    Searcher.solve_captcha(provider)
                                pass
                            if suffix is not None:
                                break
                            tries += 1
                        if not suffix:
                            if provider == "APKDONE":
                                suffix = CLI.input(f"Enter the tag for {str(provider)}: ")
                                if suffix is None:
                                    exit()
                                origin = f"https://apkdone.com/{suffix}"
                            else:
                                origin = CLI.input(
                                    f"Enter the origin for {str(provider)}: "
                                )
                                suffix = CLI.input(f"Enter the tag for {str(provider)}: ")
                        self.__variables["providers"].append(
                            LinkSuffixProvider(
                                origin=origin,
                                provider_name=provider,
                                provider=provider,
                                suffix=suffix,
                            )
                        )
                    case "HrefFinder":
                        provider_name = CLI.input(
                            "Enter the provider name: ",
                            suggestions=providers_autocomplete,
                        )
                        if provider_name is None:
                            exit()
                        link = CLI.input("Enter the link: ")
                        if link is None:
                            exit()
                        include_words = CLI.multiline_input(
                            "Enter the include words (one per line)"
                        )
                        exclude_words = CLI.multiline_input(
                            "Enter the exclude words (one per line)"
                        )
                        self.__variables["providers"].append(
                            HrefFinderProvider(
                                origin=link,
                                provider_name=provider_name,
                                link=link,
                                include_words=include_words,
                                exclude_words=exclude_words,
                            )
                        )
                    case "DirectLink":
                        provider_name = CLI.input(
                            "Enter the provider name: ",
                            suggestions=providers_autocomplete,
                        )
                        link = CLI.input("Enter the link: ")
                        self.__variables["providers"].append(
                            DirectLinkProvider(
                                origin=link,
                                provider_name=provider_name,
                                link=link,
                            )
                        )
            else:
                break

    def __get_dependencies(self) -> None:
        self.existing_apps = self.__threads["existing_apps"].result()
        dependencies = CLI.checkbox(
            title="App Dependencies",
            message="Select the app dependencies",
            options=self.existing_apps,
        )
        self.__variables["dependencies"] = dependencies

    def __get_complements(self) -> None:
        self.existing_apps = self.__threads["existing_apps"].result()
        complements = CLI.checkbox(
            title="App Complements",
            message="Select the app complements",
            options=self.existing_apps,
        )
        self.__variables["complements"] = complements

    def __get_features(self) -> None:
        self.features = self.__threads["features"].result()
        features = CLI.multiline_input(
            "Enter the features (one per line)\n",
            suggestions=self.features,
        )
        if features is None:
            exit()
        self.__variables["features"] = features

    def select_category(self):
        categories = {}
        with open(GLOBAL.Paths.Files.Categories, "r") as file:
            categories = json.load(file)
        category = CLI.select(
            title="Select Category",
            message="Select the category to add the app",
            options=list(categories.keys()),
        )
        if category is None:
            while True:
                category = CLI.input("Enter the category: ")
                if category in categories.keys():
                    CLI.message(
                        title="Invalid Category",
                        message="The category already exists",
                        type=StyleType.ERROR,
                    )
                    break
                icon = CLI.input("Enter the category icon url: ")
                categories[category] = {
                    "apps": [self.__variables["name"]],
                    "icon": icon,
                }
                break
        else:
            categories[category]["apps"].append(self.__variables["name"])
        with open(GLOBAL.Paths.Files.Categories, "w") as file:
            json.dump(categories, file, indent=4)

    def __call__(self):
        ASSIGNMENTS = {
            "name": self.__get_name,
            "icon": self.__get_icon,
            "dependencies": self.__get_dependencies,
            "complements": self.__get_complements,
            "features": self.__get_features,
            "providers": self.__get_providers,
        }

        for key, fun in ASSIGNMENTS.items():
            while self.__variables.get(key) is None:
                fun()
                self.__save_config()

        writter = Writter(
            app_name=self.__variables["name"],
            app_icon=self.__variables["icon"],
            depends=self.__variables["dependencies"],
            complements=self.__variables["complements"],
            features=self.__variables["features"],
            providers=self.__variables["providers"],
        )

        self.select_category()

        writter.write_apps()
        writter.write_index()


