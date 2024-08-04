from typing import Dict
import os
from LIB.Github import Github
from LIB.Apk import Apk
from LIB.AppUtils import AppUtils
from GLOBAL import GLOBAL
from datetime import datetime


class AppBase:
    def __init__(self, app_title: str, providers: Dict[str, callable]):
        self.app_title = app_title
        self.providers = providers
        GLOBAL.Log(f"Starting {self.app_title}", level="INFO")

    def download(self, provider_title: str, fun: callable) -> str | None:
        path = None
        try:
            path = fun()
        except Exception as e:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title}: update failed\n{str(e)}\n",
                level="ERROR",
                exception=True,
            )
            try:
                path = fun()
            except Exception as e:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title}: update failed\n{str(e)}\n",
                    level="CRITICAL",
                    exception=True,
                )
        return path

    def make_file_name(self, provider_title: str) -> str:
        return (
            AppUtils.filter_name(f"{self.app_title}_{provider_title}")
            + f"_{datetime.now().strftime('%Y%m%d')}.apk",
        )

    def move_file(self, path: str, provider_title: str) -> str:
        newFileName = os.path.join(
            GLOBAL.Paths.Directories.Apps,
            AppUtils.filter_name(f"{self.app_title}_{provider_title}") + ".apk",
        )
        if os.path.exists(newFileName) and path != newFileName:
            os.remove(newFileName)
        os.rename(path, newFileName)
        return newFileName

    def parse_apk(self, path: str) -> Apk | None:
        try:
            return Apk(path)
        except Exception as e:
            GLOBAL.Log(
                f"Failed to parse {path}\n{str(e)}\n",
                level="ERROR",
                exception=True,
            )
            return None

    def force_analyze(self, provider_title: str, path: str, apk: Apk) -> None:
        previous = GLOBAL.VirusTotal.check_previous_submissions(path, apk.sha256)
        if previous is None:
            GLOBAL.VirusTotal.add(self.app_title, provider_title, path, apk.sha256)
        else:
            if previous:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title} is infected",
                    level="CRITICAL",
                )
                GLOBAL.Index[self.app_title]["providers"][provider_title][
                    "safe"
                ] = False
                GLOBAL.Index.write()
            else:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title} is safe",
                    level="INFO",
                )
                GLOBAL.Index[self.app_title]["providers"][provider_title]["safe"] = True
                GLOBAL.Index.write()

    def process(self, provider_title: str, apk: Apk, path: str) -> None:
        oldProvider = GLOBAL.Index[self.app_title]["providers"][provider_title]
        if apk.packageName != oldProvider["packageName"]:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title} has different package name. Expected: {oldProvider['packageName']}, got: {apk.packageName}",
                level="CRITICAL",
            )

        download = None
        new_version = oldProvider["sha256"] != apk.sha256

        if GLOBAL.Args.virustotal:
            self.force_analyze(provider_title, path, apk)
        if GLOBAL.Args.github:
            download = Github.push_release(path)

        if not GLOBAL.Args.virustotal and not GLOBAL.Args.github and not new_version:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title} is up to date",
                level="INFO",
            )
            return

        if new_version and not GLOBAL.Args.virustotal:
            GLOBAL.VirusTotal.add(self.app_title, provider_title, path, apk.sha256)

        if new_version and not GLOBAL.Args.github:
            download = Github.push_release(path)

        if download is not None:
            GLOBAL.Index[self.app_title]["providers"][provider_title][
                "download"
            ] = download

        GLOBAL.Index[self.app_title]["providers"][provider_title][
            "packageName"
        ] = apk.packageName
        GLOBAL.Index[self.app_title]["providers"][provider_title][
            "version"
        ] = apk.version
        GLOBAL.Index[self.app_title]["providers"][provider_title]["sha256"] = apk.sha256

        if not new_version:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title} updated forcefully",
                level="INFO",
            )
        elif oldProvider["version"] < apk.version:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title} updated from {oldProvider['version']} to {apk.version}",
                level="INFO",
            )
        else:
            GLOBAL.Log(
                f"{self.app_title} - {provider_title} has a different SHA256",
                level="INFO",
            )

    def update(self):
        for provider_title, fun in self.providers.items():
            GLOBAL.Log(f"Updating {self.app_title} - {provider_title}", level="INFO")
            path = self.download(provider_title, fun)
            if path is None:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title}: download failed",
                    level="CRITICAL",
                )
                continue
            try:
                newFileName = self.move_file(path, provider_title)
            except Exception as e:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title}: moving failed\n{str(e)}\n",
                    level="CRITICAL",
                    exception=True,
                )
                continue

            apk = self.parse_apk(newFileName)
            if apk is None:
                GLOBAL.Log(
                    f"{self.app_title} - {provider_title}: parsing failed",
                    level="CRITICAL",
                )
                continue
            self.process(provider_title, apk, newFileName)
            GLOBAL.Index.write()
