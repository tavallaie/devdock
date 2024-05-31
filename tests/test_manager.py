import unittest
from unittest.mock import patch, MagicMock
from devdock.manager import DevContainerManager


class TestDevContainerManager(unittest.TestCase):
    def setUp(self):
        self.manager = DevContainerManager()

    @patch("devdock.manager.docker.from_env")
    def test_create_container(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.run.return_value = mock_container

        container = self.manager.create_container("python:3.9", "test_container")
        mock_client.containers.run.assert_called_with(
            "python:3.9", name="test_container", volumes={}, detach=True
        )
        self.assertEqual(container, mock_container)

    @patch("devdock.manager.docker.from_env")
    def test_start_container(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        self.manager.start_container("test_container")
        mock_container.start.assert_called_once()

    @patch("devdock.manager.docker.from_env")
    def test_stop_container(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        self.manager.stop_container("test_container")
        mock_container.stop.assert_called_once()

    @patch("devdock.manager.docker.from_env")
    def test_remove_container(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        self.manager.remove_container("test_container")
        mock_container.remove.assert_called_once()

    @patch("devdock.manager.docker.from_env")
    def test_create_volume(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_volume = MagicMock()
        mock_client.volumes.create.return_value = mock_volume

        volume = self.manager.create_volume("test_volume")
        mock_client.volumes.create.assert_called_with(name="test_volume")
        self.assertEqual(volume, mock_volume)

    @patch("devdock.manager.docker.from_env")
    def test_remove_volume(self, mock_docker):
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume

        self.manager.remove_volume("test_volume")
        mock_volume.remove.assert_called_once()


if __name__ == "__main__":
    unittest.main()
