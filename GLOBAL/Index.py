from typing import Dict, Any
import json
from dataclasses import dataclass, field, asdict


@dataclass
class IndexProvider:
    source: str = field(default="")
    version: str = field(default="")
    packageName: str = field(default="")
    download: str = field(default="")
    safe: bool = field(default=True)
    sha256: str = field(default="")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)


@dataclass
class IndexApp:
    icon: str
    providers: dict[str, IndexProvider] = field(default_factory=dict)
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
        with open(
            "/home/anfreire/Documents/UpdateMe/Scrapping/index.json", "w"
        ) as index_file:
            json.dump(self.to_dict(), index_file, indent=4)

    def to_dict(self) -> dict:
        return {app: asdict(self.index[app]) for app in self.index}

    def read(self) -> None:
        with open(self.index_file, "r") as index_file:
            raw_index: dict = json.load(index_file)
        self.index = {
            app_title: IndexApp(
                icon=app_data["icon"],
                providers=app_data["providers"],
                depends=app_data["depends"],
                complements=app_data["complements"],
                features=app_data["features"],
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

    def __contains__(self, key: str) -> bool:
        return key in self.index

    def keys(self):
        return self.index.keys()

    def values(self):
        return self.index.values()

    def items(self):
        return self.index.items()
