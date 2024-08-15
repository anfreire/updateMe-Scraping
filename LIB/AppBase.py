from typing import Dict
import os
from LIB.Github import Github
from LIB.Apk import Apk
from LIB.AppUtils import AppUtils, AnalysisStatus, AppDiff
from GLOBAL import GLOBAL, IndexProvider
from time import sleep


class AppBase:
    def __init__(self, app_title: str, providers: Dict[str, callable]):
        self.app_title = app_title
        self.providers = providers
        GLOBAL.Log(f"Starting {self.app_title}", level="INFO")

    def __download(self, provider_title: str, fun: callable) -> str | None:
        path = None
        tries = 0
        while path is None and tries < 2:
            try:
                path = fun()
            except Exception as e:
                GLOBAL.Log(
                    f"{self.app_title} from {provider_title} failed to download. Try nº{tries + 1}\n{e.__class__.__name__}: {e.args}",
                    level="ERROR",
                    exception=GLOBAL.Args.debug,
                )
                sleep(tries := tries + 1)
        return path

    def __move_file(self, provider_title: str, path: str) -> str | None:
        new_file_name = (
            AppUtils.filter_name(f"{self.app_title}_{provider_title}") + ".apk"
        )
        tries = 0
        new_path = None
        while new_path is None and tries < 3:
            try:
                new_path = AppUtils.move_file(path, new_file_name)
            except Exception as e:
                GLOBAL.Log(
                    f"{self.app_title} from {provider_title} failed to move. Try nº{tries + 1}\nException: {e.__class__.__name__}",
                    level="ERROR",
                    exception=GLOBAL.Args.debug,
                )
                sleep(tries := tries + 1)
        return new_path

    def __parse_apk(self, provider_title: str, path: str) -> Apk | None:
        try:
            return Apk(path)
        except Exception as e:
            GLOBAL.Log(
                f"{self.app_title} from {provider_title} failed to parse\nException: {e.__class__.__name__}",
                level="ERROR",
                exception=GLOBAL.Args.debug,
            )
            return None

    def __analyze(self, provider_title: str, path: str, apk: Apk) -> None:
        app_status = AppUtils.get_analysis_status(path, apk)
        if app_status == AnalysisStatus.PENDING:
            GLOBAL.VirusTotal.add(self.app_title, provider_title, path, apk.sha256)
            return
        is_safe, log_keyword, log_level = (
            (False, "infected", "CRITICAL")
            if app_status == AnalysisStatus.INFECTED
            else (True, "safe", "INFO")
        )
        GLOBAL.Index[self.app_title]["providers"][provider_title]["safe"] = is_safe
        GLOBAL.Index.write()
        GLOBAL.Log(
            f"{self.app_title} from {provider_title} is {log_keyword}",
            level=log_level,
        )

    def __process(self, provider_title: str, apk: Apk, path: str) -> None:
        provider = IndexProvider(
            **GLOBAL.Index[self.app_title]["providers"][provider_title]
        )
        app_status = AppUtils.get_app_status(provider, apk)
        analyze, push = GLOBAL.Args.virustotal, GLOBAL.Args.github

        match app_status:
            case AppDiff.NONE:
                if not analyze and not push:
                    GLOBAL.Log(
                        f"{self.app_title} from {provider_title} is up to date",
                        level="INFO",
                    )
                    return
                else:
                    GLOBAL.Log(
                        f"{self.app_title} from {provider_title} updated forcefully",
                        level="INFO",
                    )
            case AppDiff.SHA256:
                GLOBAL.Log(
                    f"{self.app_title} from {provider_title} has a different SHA256",
                    level="INFO",
                )
                analyze, push = True, True
            case AppDiff.VERSION:
                GLOBAL.Log(
                    f"{self.app_title} from {provider_title} updated from {provider['version']} to {apk.version}",
                    level="INFO",
                )
                analyze, push = True, True
            case AppDiff.PACKAGE_NAME:
                GLOBAL.Log(
                    f"{self.app_title} from {provider_title} has different package name. Expected: {provider['packageName']}, got: {apk.packageName}",
                    level="CRITICAL",
                )
                analyze, push = True, True

        if analyze:
            self.__analyze(provider_title, path, apk)

        if push:
            GLOBAL.Index[self.app_title]["providers"][provider_title]["download"] = (
                Github.push_release(path)
            )

        GLOBAL.Index[self.app_title]["providers"][provider_title][
            "packageName"
        ] = apk.packageName
        GLOBAL.Index[self.app_title]["providers"][provider_title][
            "version"
        ] = apk.version
        GLOBAL.Index[self.app_title]["providers"][provider_title]["sha256"] = apk.sha256

        GLOBAL.Index.write()

    def __update_provider(self, provider_title: str, fun: callable) -> None:
        GLOBAL.Log(f"Updating {self.app_title} from {provider_title}", level="INFO")

        path = self.__download(provider_title, fun)
        if path is None:
            GLOBAL.Log(
                f"{self.app_title} from {provider_title}: Aborted due to download failure",
                level="CRITICAL",
            )
            return

        new_path = self.__move_file(provider_title, path)
        if new_path is None:
            GLOBAL.Log(
                f"{self.app_title} from {provider_title}: Aborted due to moving failure",
                level="CRITICAL",
            )
            return

        apk = self.__parse_apk(provider_title, new_path)
        if apk is None:
            GLOBAL.Log(
                f"{self.app_title} from {provider_title}: Aborted due to parsing failure",
                level="CRITICAL",
            )
            return

        self.__process(provider_title, apk, new_path)

    def update(self):
        for provider_title, fun in self.providers.items():
            AppUtils.clean_directory(os.path.join(os.path.expanduser("~"), "Downloads"))
            self.__update_provider(provider_title, fun)
        GLOBAL.Index.write()
