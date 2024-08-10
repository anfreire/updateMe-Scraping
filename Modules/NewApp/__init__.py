from GLOBAL import GLOBAL, IndexApp, IndexProvider, LogLevel
from Modules.NewApp.Writter import (
    GithubProvider,
    LinkSuffixProvider,
    HrefFinderProvider,
    DirectLinkProvider,
    Writter,
)
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion
from LIB.Github import Github
from LIB.Thread import Thread
import pickle
import os
import requests
from typing import TypedDict, Literal, List, Tuple
from copy import deepcopy
import json
from prompt_toolkit.shortcuts import (
    yes_no_dialog,
    message_dialog,
    radiolist_dialog,
    checkboxlist_dialog,
)
from prompt_toolkit import prompt
import re


class MyCompleter(Completer):
    def __init__(self, words_list):
        self.words_list = words_list

    def get_completions(self, document, complete_event):
        current_line = document.current_line_before_cursor.lower()
        suggestions = [
            word for word in self.words_list if word.lower().startswith(current_line)
        ]
        for suggestion in suggestions:
            yield Completion(suggestion, start_position=0)


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
        if yes_no_dialog(
            title="Restore previous session?",
            text="Do you want to restore the previous session?",
        ).run():
            self.__read_config()

    def __get_name(self) -> None:
        value = ""
        self.existing_apps = self.__threads["existing_apps"].result()
        while True:
            value = prompt("Enter the app name: ")
            if value is None:
                exit()
            value = value.strip()
            if len(value) == 0:
                message_dialog(
                    title="Invalid Name",
                    text="The name cannot be empty",
                    style=Style.from_dict({"bg": "#ff0000"}),
                ).run()
                continue
            if any(value == app for app in self.existing_apps):
                message_dialog(
                    title="Invalid Name",
                    text="The name already exists",
                    style=Style.from_dict({"bg": "#ff0000"}),
                ).run()
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
                if yes_no_dialog(
                    title="Icon already exists",
                    text="Do you want to use it?",
                ).run():
                    self.__variables["icon"] = iconPath
                    break
                else:
                    if yes_no_dialog(
                        title="Remove existing icon",
                        text="Do you want to remove the existing icon?",
                    ).run():
                        os.remove(iconPath)
                    else:
                        continue
            icon = prompt("Enter the app icon url: ")
            if icon is None:
                exit()
            icon = icon.strip()
            if len(icon) == 0:
                message_dialog(
                    title="Invalid Icon",
                    text="The icon cannot be empty",
                    style=Style.from_dict({"bg": "#ff0000"}),
                ).run()
                continue
            response = None
            try:
                response = requests.get(icon)
            except Exception:
                pass
            if response is None or response.status_code != 200:
                message_dialog(
                    title="Invalid Icon",
                    text="The icon url is invalid",
                    style=Style.from_dict({"bg": "#ff0000"}),
                ).run()
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
            if yes_no_dialog(
                title="Add Provider",
                text="Do you want to add a provider?",
            ).run():
                provider = radiolist_dialog(
                    title="Select Provider",
                    text="Select the provider to add",
                    values=[
                        (x, x)
                        for x in ["Github", "LinkSuffix", "HrefFinder", "DirectLink"]
                    ],
                ).run()
                if provider is None:
                    exit()
                match provider:
                    case "Github":
                        user = prompt(
                            "Enter the Github user: ", completer=MyCompleter(providers_autocomplete)
                        )
                        if user is None:
                            exit()
                        repo = prompt("Enter the Github repo: ")
                        if repo is None:
                            exit()
                        include_words = prompt(
                            "Enter the include words (one per line)", multiline=True
                        )
                        if include_words is None:
                            exit()
                        include_words = include_words.split("\n")
                        include_words = [
                            word for word in include_words if len(word.strip())
                        ]
                        exclude_words = prompt(
                            "Enter the exclude words (one per line)", multiline=True
                        )
                        if exclude_words is None:
                            exit()
                        exclude_words = exclude_words.split("\n")
                        exclude_words = [
                            word for word in exclude_words if len(word.strip())
                        ]
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
                        provider = radiolist_dialog(
                            title="Select Provider",
                            text="Select the provider to add",
                            values={
                                "MODYOLO": "MODYOLO",
                                "LITEAPKS": "LITEAPKS",
                                "APKDONE": "APKDONE",
                            },
                        ).run()
                        if provider is None:
                            exit()
                        suffix = prompt(f"Enter the tag for {provider}")
                        if suffix is None:
                            exit()
                        origin = prompt(f"Enter the origin for {provider}")
                        if origin is None:
                            exit()
                        self.__variables["providers"].append(
                            LinkSuffixProvider(
                                origin=origin,
                                provider_name=provider,
                                provider=provider,
                                suffix=suffix,
                            )
                        )
                    case "HrefFinder":
                        provider_name = prompt(
                            "Enter the provider name: ",
                            completer=MyCompleter(providers_autocomplete),
                        )
                        if provider_name is None:
                            exit()
                        link = prompt("Enter the link: ")
                        if link is None:
                            exit()
                        include_words = prompt(
                            "Enter the include words (one per line)", multiline=True
                        )
                        if include_words is None:
                            exit()
                        include_words = include_words.split("\n")
                        include_words = [
                            word for word in include_words if len(word.strip())
                        ]
                        exclude_words = prompt(
                            "Enter the exclude words (one per line)", multiline=True
                        )
                        if exclude_words is None:
                            exit()
                        exclude_words = exclude_words.split("\n")
                        exclude_words = [
                            word for word in exclude_words if len(word.strip())
                        ]
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
                        provider_name = prompt(
                            "Enter the provider name: ",
                            completer=MyCompleter(providers_autocomplete),
                        )
                        if provider_name is None:
                            exit()
                        link = prompt("Enter the link: ")
                        if link is None:
                            exit()
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
        dependencies = checkboxlist_dialog(
            title="App Dependencies",
            text="Select the app dependencies",
            values=[(app, app) for app in self.existing_apps],
        ).run()
        if dependencies is None:
            exit()
        self.__variables["dependencies"] = dependencies

    def __get_complements(self) -> None:
        self.existing_apps = self.__threads["existing_apps"].result()
        complements = checkboxlist_dialog(
            title="App Complements",
            text="Select the app complements",
            values=[(app, app) for app in self.existing_apps],
        ).run()
        if complements is None:
            exit()
        self.__variables["complements"] = complements

    def __get_features(self) -> None:
        self.features = self.__threads["features"].result()
        features = prompt(
            "Enter the features (one per line)\n",
            completer=MyCompleter(self.features),
            multiline=True,
        )
        if features is None:
            exit()
        features = features.split("\n")
        features = [feature for feature in features if len(feature.strip())]
        self.__variables["features"] = features

    def select_category(self):
        categories = {}
        with open(GLOBAL.Paths.Files.Categories, "r") as file:
            categories = json.load(file)
        category = radiolist_dialog(
            title="Select Category",
            text="Select the category to add the app",
            values=[(category, category) for category in categories.keys()],
        ).run()
        if category is None:
            while True:
                category = prompt("Enter the category: ")
                if category in categories.keys():
                    message_dialog(
                        title="Invalid Category",
                        text="The category already exists",
                        style=Style.from_dict({"bg": "#ff0000"}),
                    ).run()
                    break
                icon = prompt("Enter the category icon url: ")
                categories[category] = {
                    "apps": [self.__variables["name"]],
                    "icon": icon,
                }
                break
        else:
            categories[category]["apps"].append(self.__variables["name"])
        with open(GLOBAL.Paths.Files.Categories, "w") as file:
            json.dump(categories, file, indent=4)
        Github.push_categories()

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

        self.__remove_config()
