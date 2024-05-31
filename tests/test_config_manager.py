import unittest
import os
import shutil
from devdock.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.config_manager = ConfigManager()
        self.config_name = "test_config"
        self.config_data = {
            "type": "container",
            "name": "test_container",
            "image": "python:3.9",
            "volumes": ["/host/path:/container/path"],
        }

    def tearDown(self):
        config_path = self.config_manager.get_config_path(self.config_name)
        if os.path.exists(config_path):
            os.remove(config_path)
        if os.path.exists(self.config_manager.CONFIG_BASE_DIR):
            shutil.rmtree(self.config_manager.CONFIG_BASE_DIR)

    def test_create_and_read_config(self):
        self.config_manager.create_config(self.config_name, self.config_data)
        read_config = self.config_manager.read_config(self.config_name)
        self.assertEqual(self.config_data, read_config)

    def test_delete_config(self):
        self.config_manager.create_config(self.config_name, self.config_data)
        self.config_manager.delete_config(self.config_name)
        with self.assertRaises(FileNotFoundError):
            self.config_manager.read_config(self.config_name)

    def test_list_configs(self):
        self.config_manager.create_config(self.config_name, self.config_data)
        configs = self.config_manager.list_configs()
        self.assertIn(self.config_name, configs)


if __name__ == "__main__":
    unittest.main()
