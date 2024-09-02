import tomllib
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = {}
        with open('general.toml', 'r') as file:
            self.config = tomllib.loads(file.read())

    def get(self, section, key):
        return self.config[section][key]