import configparser


class Config:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def __getitem__(self, section: str):
        return self.config[section]

    def get(self, section: str, key: str):
        try:
            return self.config[section][key]
        except KeyError:
            return None

    def set(self, section: str, key: str, value: str):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.config_file, "w") as file:
            self.config.write(file)
