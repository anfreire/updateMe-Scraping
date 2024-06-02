import vt
from dataclasses import dataclass
from GLOBAL import GLOBAL
from typing import List
import time
from typing import Generator


@dataclass
class Analysis:
    analysis: vt.Object
    appname: str
    provider: str
    sha256: str
    path: str
    infected: bool
    finished: bool


class VirusTotal:
    istance = None
    client = None
    queue = List[Analysis]
    requests_made = 0
    last_minute = None

    def __new__(cls):
        if not cls.istance:
            cls.istance = super(VirusTotal, cls).__new__(cls)
            cls.client = vt.Client(GLOBAL.Config["VirusTotal"]["API_KEY"])
            cls.queue: List[Analysis] = []
            cls.requests_made = 0
            cls.last_minute = None
        return cls.istance

    def __del__(cls) -> None:
        cls.client.close()

    @classmethod
    def _add(cls, path: str) -> vt.Object:
        with open(path, "rb") as file:
            return cls.client.scan_file(file)

    @classmethod
    def can_make_request(cls) -> bool:
        if cls.last_minute is None or time.time() - cls.last_minute > 60:
            return True
        return cls.requests_made < 4

    @classmethod
    def register_request(cls) -> None:
        if cls.last_minute is None or time.time() - cls.last_minute > 60:
            cls.last_minute = time.time()
            cls.requests_made = 1
        else:
            cls.requests_made += 1

    @classmethod
    def wait_requests_available(cls) -> None:
        printed = False
        while not cls.can_make_request():
            if not printed:
                GLOBAL.Log(
                    "VirusTotal rate limit reached, waiting for requests to be available",
                    level="INFO",
                )
                printed = True
            time.sleep(1)

    @classmethod
    def add(cls, appname: str, provider: str, path: str, sha256: str) -> None:
        cls.wait_requests_available()
        cls.register_request()
        analysis = cls._add(path)
        cls.queue.append(
            Analysis(analysis, appname, provider, sha256, path, False, False)
        )
        GLOBAL.Log(f"Added {appname} - {provider} to VirusTotal queue", level="INFO")

    @classmethod
    def update_analysis(cls, data: Analysis) -> None:
        cls.wait_requests_available()
        cls.register_request()
        data.analysis = cls.client.get_object("/analyses/{}", data.analysis.id)

    @classmethod
    def is_finished(cls, data: Analysis) -> bool:
        return data.analysis.status == "completed"

    @classmethod
    def has_virus(cls, data: Analysis) -> bool:
        return any(
            [data.analysis.stats["malicious"], data.analysis.stats["suspicious"]]
        )

    @classmethod
    def wait_queue(cls) -> Generator[Analysis, None, None]:
        done = []
        while len(cls.queue) and len(done) != len(cls.queue):
            for data in cls.queue:
                if data in done:
                    continue
                cls.update_analysis(data)
                if not cls.is_finished(data):
                    continue
                done.append(data)
                data.finished = True
                if cls.has_virus(data):
                    data.infected = True
                    yield data
                    GLOBAL.Log(
                        f"{data.appname} - {data.provider} is infected", level="WARNING"
                    )
                else:
                    yield data
                    GLOBAL.Log(
                        f"{data.appname} - {data.provider} is safe", level="INFO"
                    )
