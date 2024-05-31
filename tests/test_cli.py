import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from devdock.cli import cli


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("devdock.manager.DevContainerManager.create_dev_container")
    @patch("devdock.manager.docker.from_env", return_value=MagicMock())
    def test_mkdevcontainer(self, mock_docker, mock_create):
        mock_container = MagicMock()
        mock_container.name = "test_container"
        mock_container.id = "12345"
        mock_create.return_value = mock_container
        result = self.runner.invoke(
            cli, ["mkdevcontainer", "--image", "python:3.9", "--name", "test_container"]
        )
        print("CLI Output (mkdevcontainer):", result.output)  # Debugging line
        self.assertIn(
            "Dev container test_container created with ID 12345.", result.output
        )
        mock_create.assert_called_once_with("test_container", "python:3.9", [])

    @patch("devdock.manager.DevContainerManager.create_dev_compose")
    @patch("devdock.manager.docker.from_env", return_value=MagicMock())
    def test_mkdevcompose(self, mock_docker, mock_create):
        mock_create.return_value = MagicMock()
        result = self.runner.invoke(
            cli,
            [
                "mkdevcompose",
                "--compose-file",
                "docker-compose.yml",
                "--name",
                "test_compose",
            ],
        )
        print("CLI Output (mkdevcompose):", result.output)  # Debugging line
        self.assertIn(
            "Dev compose configuration test_compose created and services started.",
            result.output,
        )
        mock_create.assert_called_once_with("test_compose", "docker-compose.yml")

    @patch("devdock.manager.DevContainerManager.remove_dev_container")
    @patch("devdock.config.config_manager.ConfigManager.read_config")
    @patch("devdock.manager.docker.from_env", return_value=MagicMock())
    def test_rmdev_container(self, mock_docker, mock_read, mock_remove):
        mock_read.return_value = {"type": "container"}
        result = self.runner.invoke(cli, ["rmdev", "test_container"])
        print("CLI Output (rmdev container):", result.output)  # Debugging line
        self.assertIn("Dev configuration test_container removed.", result.output)
        mock_remove.assert_called_once_with("test_container")

    @patch("devdock.manager.DevContainerManager.remove_dev_compose")
    @patch("devdock.config.config_manager.ConfigManager.read_config")
    @patch("devdock.manager.docker.from_env", return_value=MagicMock())
    def test_rmdev_compose(self, mock_docker, mock_read, mock_remove):
        mock_read.return_value = {"type": "compose"}
        result = self.runner.invoke(cli, ["rmdev", "test_compose"])
        print("CLI Output (rmdev compose):", result.output)  # Debugging line
        self.assertIn("Dev configuration test_compose removed.", result.output)
        mock_remove.assert_called_once_with("test_compose")

    @patch("devdock.manager.DevContainerManager.activate_dev")
    @patch("devdock.manager.docker.from_env", return_value=MagicMock())
    def test_workon(self, mock_docker, mock_activate):
        mock_activate.return_value = {"name": "test_container"}
        result = self.runner.invoke(cli, ["workon", "test_container"])
        print("CLI Output (workon):", result.output)  # Debugging line
        self.assertIn("Activated dev configuration test_container.", result.output)
        mock_activate.assert_called_once_with("test_container")


if __name__ == "__main__":
    unittest.main()
