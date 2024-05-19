from base.abstract.singleton import SingletonMetaclass


class Config(metaclass=SingletonMetaclass):
    def __init__(
        self,
        vt: bool = False,
        git: bool = False,
    ) -> None:
        self.vt = vt
        self.git = git
