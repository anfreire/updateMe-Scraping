from GLOBAL.Paths import Paths
from GLOBAL.Args import Args
from GLOBAL.Log import Log, LogLevel
from GLOBAL.Config import Config
from GLOBAL.VirusTotal import VirusTotal, VirusTotalAnalysis
from GLOBAL.Index import Index, IndexProvider, IndexProviders, IndexApp


class Global:
    def __init__(self):
        self.Paths = Paths()
        self.Args = Args.parse_args()
        self.Log = Log(self.Paths.Files.Log, self.Args.debug)
        self.Config = Config(self.Paths.Files.Config)
        self.VirusTotal = VirusTotal(self.Config["VirusTotal"]["API_KEY"], self.Log)
        self.Log("Global instance created")
        self.Log(f"Args: {self.Args.__dict__}")


GLOBAL = Global()


def Global(*args, **kwargs):
    raise TypeError("Global is not meant to be instantiated more than once.")
