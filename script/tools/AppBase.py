from tools.Index import Index, ProvidersType
from tools.Downloader import Downloader
from typing import Literal, Dict, Tuple
from utils.github import Github
from lib.apk import Apk
from constants import PATHS
from lib.virustotal import VirusTotal

vt = VirusTotal()


ProvidesFunType = Dict[str, callable]


class AppBase:
    def __init__(self, app_title: str, providers: ProvidesFunType):
        self.app_title = app_title
        self.providers = providers

    def make_file_name(self, provider_title: str) -> str:
        title = self.app_title.replace(" ", "_").lower()
        provider = provider_title.replace(" ", "_").lower()
        return f"{title}_{provider}.apk".replace("(", "").replace(")", "")

    def get_link(self, providerTitle: str, fun: callable) -> str | tuple | None:
        link = None
        try:
            link = fun()
        except Exception as e:
            print(f"{self.app_title} - {providerTitle} failed to get link\n{str(e)}")
            pass
        if link is None:
            print(f"{self.app_title} - {providerTitle} failed to get link")
        return link

    def download(
        self, link: str, provider_title: str, origin: str = None, manual: bool = False
    ) -> Tuple[bool, str]:
        path = PATHS.APPS_DIR + "/" + self.make_file_name(provider_title)
        res = False
        if not manual:
            res = Downloader.download_requests(link, path)
            if not res:
                res = Downloader.download_curl(link, path, origin)
        if not res:
            res = Downloader.download_chrome(link, path)
        return (res, path)

    def process(self, provider_title: str, link: str, path: str, index: Index) -> bool:
        apk = Apk(path)
        old_provider = index.get_provider(self.app_title, provider_title)
        if old_provider["sha256"] != apk.sha256:
            vt.add(self.app_title, provider_title, path, apk.sha256)
            download = Github.push_release(path)
            index.update_provider(
                self.app_title, provider_title, apk.version, link, download, apk.sha256
            )
            if old_provider["version"] < apk.version:
                print(
                    f"{self.app_title} - {provider_title}updated from {old_provider['version']} to {apk.version}"
                )
            else:
                print(f"{self.app_title} - {provider_title}got bug fix")
            return True
        else:
            print(f"{self.app_title} - {provider_title}already up to date")
            return False

    def _update(self, provider_title, fun, index):
        link = None
        origin = None
        res = self.get_link(provider_title, fun)
        if isinstance(res, tuple):
            link = res[0]
            origin = res[1]
        else:
            link = res
        result = False
        if link:
            path = self.download(link, provider_title, origin)
            try:
                if path[0]:
                    result = self.process(provider_title, link, path[1], index)
            except:
                path = self.download(link, provider_title, origin, manual=True)
                if path[0]:
                    result = self.process(provider_title, link, path[1], index)
        return (path[1], result)

    def update(self, index: Index) -> None:
        for provider_title, fun in self.providers.items():
            try:
                path, result = self._update(provider_title, fun, index)
                index.write()
            except Exception as e:
                print(f"{self.app_title} - {provider_title}: update failed\n{str(e)}\n")

    def add(self, index: Index) -> None:
        for provider_title, fun in self.providers.items():
            link = None
            origin = None
            res = self.get_link(provider_title, fun)
            if isinstance(res, tuple):
                link = res[0]
                origin = res[1]
            else:
                link = res
            if link:
                path = self.download(link, provider_title, origin)
            if path[0]:
                path = path[1]
                apk = Apk(path)
                vt.add(self.app_title, provider_title, path, apk.sha256)
                source = input(
                    f"Enter source for {self.app_title} - {provider_title}: "
                )
                version = apk.version
                link = link
                packageName = apk.packageName
                download = Github.push_release(path)
                provider: ProvidersType = {
                    "packageName": packageName,
                    "source": source,
                    "version": version,
                    "link": link,
                    "download": download,
                    "sha256": apk.sha256,
                    "safe": True,
                }
                index.add_provider(self.app_title, provider_title, provider)
                index.write()
                print(f"{self.app_title} - {provider_title} added")

