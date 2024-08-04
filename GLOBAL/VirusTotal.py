import vt
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Generator
import time


@dataclass
class VirusTotalAnalysis:
    analysis: vt.Object
    appname: str
    provider: str
    sha256: str
    path: str
    infected: bool
    finished: bool


class VirusTotal:
    def __init__(self, api_key: str, log: "Log") -> None:  # type: ignore
        self.client = vt.Client(api_key)
        self.log = log
        self.queue: List[VirusTotalAnalysis] = []
        self.requests_made = 0
        self.last_minute = None

    def __del__(self):
        self.client.close()

    def _add(self, path: str) -> vt.Object:
        with open(path, "rb") as file:
            return self.client.scan_file(file)

    def get_submited_file(self, sha256: str) -> vt.Object | None:
        try:
            return self.client.get_object(f"/files/{sha256}")
        except vt.error.APIError:
            return None

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
                self.log(
                    "VirusTotal rate limit reached, waiting for requests to be available",
                    level="INFO",
                )
                printed = True
            time.sleep(1)

    def check_previous_submissions(self, path: str, sha256: str) -> None | bool:
        self.wait_requests_available()
        self.register_request()
        analysis = self.get_submited_file(sha256)
        if analysis is None or not any([name in path for name in analysis.names]):
            return None
        return (
            True
            if any(
                [
                    analysis.last_analysis_stats["malicious"],
                    analysis.last_analysis_stats["suspicious"],
                ]
            )
            else False
        )

    def add(self, appname: str, provider: str, path: str, sha256: str) -> None:
        self.wait_requests_available()
        self.register_request()
        analysis = self._add(path)
        self.queue.append(
            VirusTotalAnalysis(analysis, appname, provider, sha256, path, False, False)
        )
        self.log(f"Added {appname} - {provider} to VirusTotal queue", level="INFO")

    def update_analysis(self, data: VirusTotalAnalysis) -> None:
        self.wait_requests_available()
        self.register_request()
        data.analysis = self.client.get_object("/analyses/{}", data.analysis.id)

    def is_finished(self, data: VirusTotalAnalysis) -> bool:
        return data.analysis.status == "completed"

    def has_virus(self, data: VirusTotalAnalysis) -> bool:
        return any(
            [data.analysis.stats["malicious"], data.analysis.stats["suspicious"]]
        )

    def wait_queue(self) -> Generator[VirusTotalAnalysis, None, None]:
        done = []
        while len(self.queue) and len(done) != len(self.queue):
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
                    yield data
                    self.log(
                        f"{data.appname} - {data.provider} is infected", level="WARNING"
                    )
                else:
                    yield data
                    self.log(f"{data.appname} - {data.provider} is safe", level="INFO")
