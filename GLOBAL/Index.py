from typing import Dict, Any
import json
from dataclasses import dataclass, field, asdict


@dataclass
class IndexProvider:
    source: str
    version: str
    packageName: str
    download: str = ""
    safe: bool = True
    sha256: str = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)


@dataclass
class IndexProviders:
    providers: Dict[str, IndexProvider] = field(default_factory=dict)

    def __getitem__(self, provider: str) -> IndexProvider:
        return self.providers[provider]

    def __setitem__(self, provider: str, value: IndexProvider) -> None:
        self.providers[provider] = value

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> "IndexProviders":
        return cls({k: IndexProvider(**v) for k, v in data.items()})


@dataclass
class IndexApp:
    icon: str
    providers: IndexProviders
    depends: list = field(default_factory=list)
    complements: list = field(default_factory=list)
    features: list = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)


class Index:
    def __init__(self, index_file: str):
        self.index_file = index_file
        self.index: Dict[str, IndexApp] = {}
        self.read()

    def to_dict(self) -> dict:
        return {app: asdict(self.index[app]) for app in self.index}

    def read(self) -> None:
        with open(self.index_file, "r") as index_file:
            raw_index: dict = json.load(index_file)
        self.index = {
            app_title: IndexApp(
                icon=app_data["icon"],
                providers=IndexProviders.from_dict(app_data["providers"]),
                depends=app_data.get("depends", []),
                complements=app_data.get("complements", []),
                features=app_data.get("features", []),
            )
            for app_title, app_data in raw_index.items()
        }

    def write(self) -> None:
        with open(self.index_file, "w") as index_file:
            json.dump(self.to_dict(), index_file, indent=4)

    def __getitem__(self, key: str) -> IndexApp:
        return self.index[key]

    def __setitem__(self, key: str, value: IndexApp) -> None:
        self.index[key] = value
