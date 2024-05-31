import os
import yaml

CONFIG_BASE_DIR = os.path.expanduser("~/.devdock")


class ConfigManager:
    def __init__(self):
        if not os.path.exists(CONFIG_BASE_DIR):
            os.makedirs(CONFIG_BASE_DIR)

    def get_config_path(self, name):
        return os.path.join(CONFIG_BASE_DIR, f"{name}.yaml")

    def create_config(self, name, config):
        with open(self.get_config_path(name), "w") as f:
            yaml.dump(config, f)

    def read_config(self, name):
        config_path = self.get_config_path(name)
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"No configuration found for {name}")

    def delete_config(self, name):
        os.remove(self.get_config_path(name))

    def list_configs(self):
        return [
            os.path.splitext(f)[0]
            for f in os.listdir(CONFIG_BASE_DIR)
            if f.endswith(".yaml")
        ]
