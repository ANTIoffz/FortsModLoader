import json

class Config:
    def __init__(self, config=None, path='config.json') -> None:
        if config is None:
            config = {}
        self.config = config
        self.path = path

    def read(self, config_key=None) -> any:
        try:
            with open(self.path, "r") as config_file:
                self.config = json.load(config_file)
        except(FileNotFoundError, json.JSONDecodeError):
            self.save(self.config)

        if config_key is None:
            return self.config
        else:
            return self.config.get(config_key)

    def save(self, config: dict) -> None:
        self.config = config
        try:
            with open(self.path, "w") as config_file:
                json.dump(self.config, config_file, indent=4)
        except(FileNotFoundError, IOError):
            print("Ошибка записи в файл 'config.json'")


    def update(self, key: str, value: any) -> None:
        self.config = self.read()
        self.config[key] = value
        self.save(self.config)
