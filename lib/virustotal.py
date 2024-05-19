import vt
import json
from dataclasses import dataclass
from tools.Index import Index
from typing import List
import time
from base.abstract.singleton import SingletonMetaclass
from constants import PATHS
from lib.github import Github


@dataclass
class Analysis:
    analysis: vt.Object
    appname: str
    provider: str
    sha256: str
    path: str
    infected: bool
    finished: bool


class VirusTotal(metaclass=SingletonMetaclass):

    def __init__(self) -> None:
        api_key = json.load(open(PATHS.VT_KEY))["key"]
        self.client = vt.Client(api_key)
        self.queue: List[Analysis] = []
        self.requests_made = 0
        self.last_minute = None

    def __del__(self) -> None:
        self.client.close()

    def _add(self, path: str) -> vt.Object:
        with open(path, "rb") as file:
            return self.client.scan_file(file)

    def can_make_request(self) -> bool:
        if self.last_minute is None or time.time() - self.last_minute > 60:
            return True
        return self.requests_made < 4

    def register_request(self) -> None:
        if self.last_minute is None or time.time() - self.last_minute > 60:
            self.last_minute = time.time()
            self.requests_made = 1
        else:
            self.requests_made += 1

    def wait_requests_available(self) -> None:
        printed = False
        while not self.can_make_request():
            if not printed:
                print("Waiting for VirusTotal requests to be available")
                printed = True
            time.sleep(1)

    def add(self, appname: str, provider: str, path: str, sha256: str) -> None:
        self.wait_requests_available()
        self.register_request()
        analysis = self._add(path)
        self.queue.append(
            Analysis(analysis, appname, provider, sha256, path, False, False)
        )

    def update_analysis(self, data: Analysis) -> None:
        self.wait_requests_available()
        self.register_request()
        data.analysis = self.client.get_object("/analyses/{}", data.analysis.id)

    def is_finished(self, data: Analysis) -> bool:
        return data.analysis.status == "completed"

    def has_virus(self, data: Analysis) -> bool:
        return any(
            [data.analysis.stats["malicious"], data.analysis.stats["suspicious"]]
        )

    def wait_queue(self) -> None:
        done = []
        while len(done) != len(self.queue) and len(self.queue) > 0:
            for data in self.queue:
                if data in done:
                    continue
                self.update_analysis(data)
                if not self.is_finished(data):
                    continue
                done.append(data)
                data.finished = True
                if self.has_virus(data):
                    data.infected = True
                    print(f"{data.appname} - {data.provider} is infected")
                else:
                    print(f"{data.appname} - {data.provider} is clean")

    def update_index(self, index: Index) -> None:
        for data in self.queue:
            index.update_app_safety(data.appname, data.provider, not data.infected)
        index.write()
        Github.push_index("Updated VirusTotal results")

    def get_uploaded_file(self, sha256) -> vt.Object:
        self.wait_requests_available()
        self.register_request()
        return self.client.get_object(f"/files/{sha256}")
