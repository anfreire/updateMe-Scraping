from typing import Any, Dict, Type, Protocol
import json
import importlib


class DynamicProviderClass(Protocol):
    def __init__(self, *args: Any): ...

    def __call__(self, *args: Any) -> str | None: ...


class Provider:
    class_name: str
    init_args: list
    call_args: list

    def __init__(self, class_name: str, init_args: list, call_args: list):
        self.class_name = class_name
        self.init_args = init_args
        self.call_args = call_args

    def __get_dynamic_class(self) -> Type[DynamicProviderClass]:
        module = importlib.import_module(f"Providers.{self.class_name}")
        return getattr(module, self.class_name)

    def __call__(self) -> str | None:
        dynamic_class = self.__get_dynamic_class()
        return dynamic_class(*self.init_args)(*self.call_args)


class App:
    name: str
    providers: Dict[str, Provider]

    def __init__(self, name: str, providers: Dict[str, Provider]):
        self.name = name
        self.providers = providers

    def __call__(self, providers: list[str] = None) -> None:
        from LIB.AppBase import AppBase

        app = AppBase(self.name, self.providers)
        app.update(providers)


class Apps:
    def __init__(self, apps_json: str):
        self.apps: Dict[str, App] = {}
        self.apps_json = apps_json
        self.__read(apps_json)

    def __getitem__(self, key: str) -> App:
        return self.apps[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.apps[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.apps

    def __iter__(self):
        return iter(self.apps)

    def __len__(self) -> int:
        return len(self.apps)

    def keys(self):
        return self.apps.keys()

    def values(self):
        return self.apps.values()

    def items(self):
        return self.apps.items()

    def __read(self, apps_json: str) -> None:
        with open(apps_json, "r") as file:
            apps = json.load(file)
        self.apps = {
            app: App(
                app,
                {
                    provider: Provider(
                        provider_info["class"],
                        provider_info["init_args"],
                        provider_info["call_args"],
                    )
                    for provider, provider_info in providers.items()
                },
            )
            for app, providers in apps.items()
        }

    def write(self) -> None:
        with open(self.apps_json, "w") as file:
            json.dump(
                {
                    app: {
                        provider: {
                            "class": provider_info.class_name,
                            "init_args": provider_info.init_args,
                            "call_args": provider_info.call_args,
                        }
                        for provider, provider_info in app_info.providers.items()
                    }
                    for app, app_info in self.apps.items()
                },
                file,
                indent=4,
            )
