from typing import TypedDict, Dict, List
import json
from copy import deepcopy
from constants import PATHS
import os
import hashlib


# ------------------------------
# TYPES


class ProviderType(TypedDict):
    source: str
    version: str
    link: str
    packageName: str
    download: str
    safe: bool
    sha256: str


ProvidersType = Dict[str, ProviderType]


class AppType(TypedDict):
    depends: list[str]
    complements: list[str]
    features: list[str]
    icon: str
    providers: ProvidersType


IndexType = Dict[str, AppType]

ChangesType = Dict[str, List[str]]



# ------------------------------


class Index:
    def __init__(self):
        self.oldIndex: IndexType = self.read()
        self.newIndex: IndexType = deepcopy(self.oldIndex)

    def write(self) -> None:
        with open(PATHS.INDEX, "w") as index_file:
            json.dump(self.newIndex, index_file, indent=4)

    @property
    def apps(self) -> list[str]:
        return list(self.oldIndex.keys())

    def get_app_providers(self, app: str, old=True) -> List[str]:
        return list((self.oldIndex if old else self.newIndex)[app]["providers"].keys())

    def read(self) -> IndexType:
        rawIndex = None
        with open(PATHS.INDEX, "r") as index_file:
            rawIndex = json.load(index_file)
        index: IndexType = {}
        for appTitle in rawIndex.keys():
            providers: ProvidersType = {}
            for providerTitle in rawIndex[appTitle]["providers"].keys():
                source: ProviderType = ProviderType(
                    packageName=rawIndex[appTitle]["providers"][providerTitle][
                        "packageName"
                    ],
                    source=rawIndex[appTitle]["providers"][providerTitle]["source"],
                    version=rawIndex[appTitle]["providers"][providerTitle]["version"],
                    link=rawIndex[appTitle]["providers"][providerTitle]["link"],
                    download=(
                        rawIndex[appTitle]["providers"][providerTitle]["download"]
                        if "download" in rawIndex[appTitle]["providers"][providerTitle]
                        else ""
                    ),
                    safe=(
                        rawIndex[appTitle]["providers"][providerTitle]["safe"]
                        if "safe" in rawIndex[appTitle]["providers"][providerTitle]
                        else True
                    ),
                    sha256=(
                        rawIndex[appTitle]["providers"][providerTitle]["sha256"]
                        if "sha256" in rawIndex[appTitle]["providers"][providerTitle]
                        else ""
                    ),
                )
                providers[providerTitle] = source
            app: AppType = AppType(
                icon=rawIndex[appTitle]["icon"],
                depends=(
                    rawIndex[appTitle]["depends"]
                    if "depends" in rawIndex[appTitle]
                    else []
                ),
                complements=(
                    rawIndex[appTitle]["complements"]
                    if "complements" in rawIndex[appTitle]
                    else []
                ),
                features=(
                    rawIndex[appTitle]["features"]
                    if "features" in rawIndex[appTitle]
                    else []
                ),
                providers=providers,
            )
            index[appTitle] = app
        return index

    def get_changes(self) -> ChangesType:
        changes: ChangesType = {}
        for app in self.apps:
            app_changes = []
            for provider in self.get_app_providers(app):
                if (
                    self.oldIndex[app]["providers"][provider]
                    != self.newIndex[app]["providers"][provider]
                ):
                    app_changes.append(provider)
            if len(app_changes):
                changes[app] = app_changes
        return changes

    def update_provider(
        self,
        app: str,
        provider: str,
        version: str,
        link: str,
        download: str,
        sha256: str,
    ) -> None:
        self.newIndex[app]["providers"][provider]["version"] = version
        self.newIndex[app]["providers"][provider]["link"] = link
        self.newIndex[app]["providers"][provider]["download"] = download
        self.newIndex[app]["providers"][provider]["sha256"] = sha256

    def add_provider(self, app: str, title: str, provider: ProviderType) -> None:
        self.newIndex[app]["providers"][title] = provider

    def get_provider(self, app: str, provider: str) -> ProviderType:
        return self.oldIndex[app]["providers"][provider]

    def update_app_safety(self, app: str, provider: str, safe: bool) -> None:
        self.newIndex[app]["providers"][provider]["safe"] = safe