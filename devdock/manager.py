import docker
import yaml
import subprocess
from devdock.config.config_manager import ConfigManager


class DevContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.config_manager = ConfigManager()

    def get_container(self, identifier):
        try:
            return self.client.containers.get(identifier)
        except docker.errors.NotFound:
            containers = self.client.containers.list(
                all=True, filters={"name": identifier}
            )
            if containers:
                return containers[0]
            raise docker.errors.NotFound(f"Container {identifier} not found")

    def create_container(self, image, name, volumes=None):
        try:
            self.client.images.pull(image)

            volume_bindings = {}
            if volumes:
                for volume in volumes:
                    parts = volume.split(":")
                    if len(parts) != 2:
                        raise ValueError(f"Invalid volume mapping: {volume}")
                    host_path, container_path = parts
                    volume_bindings[host_path] = {"bind": container_path, "mode": "rw"}

            container = self.client.containers.run(
                image=image,
                name=name,
                volumes=volume_bindings,
                detach=True,
                stdin_open=True,
                tty=True,
                command="/bin/sh",
            )
            return container
        except docker.errors.ImageNotFound as e:
            raise docker.errors.ImageNotFound(str(e))
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise RuntimeError(f"Failed to create container: {str(e)}")

    def create_dev_compose(self, name, compose_file, volume_mappings=None):
        try:
            compose_data = self.read_compose_file(compose_file)
            dev_compose_file = f"{compose_file.rsplit('.', 1)[0]}.dev.yaml"
            if volume_mappings:
                for mapping in volume_mappings:
                    service_name, host_path, container_path = mapping.split(":")
                    if service_name in compose_data["services"]:
                        updated_volumes = [f"{host_path}:{container_path}"]
                        if "volumes" in compose_data["services"][service_name]:
                            compose_data["services"][service_name]["volumes"].extend(
                                updated_volumes
                            )
                        else:
                            compose_data["services"][service_name]["volumes"] = (
                                updated_volumes
                            )
            self.write_compose_file(dev_compose_file, compose_data)
            self.start_compose_services(dev_compose_file)
            config = {"type": "compose", "name": name, "compose_file": dev_compose_file}
            self.config_manager.create_config(name, config)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Docker Compose file {compose_file} not found")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise RuntimeError(f"Failed to create dev compose: {str(e)}")

    def start_container(self, identifier):
        try:
            container = self.get_container(identifier)
            container.start()
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"Container {identifier} not found")
        except Exception as e:
            raise RuntimeError(f"Failed to start container: {str(e)}")

    def stop_container(self, identifier):
        try:
            container = self.get_container(identifier)
            container.stop()
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"Container {identifier} not found")
        except Exception as e:
            raise RuntimeError(f"Failed to stop container: {str(e)}")

    def remove_container(self, identifier):
        try:
            container = self.get_container(identifier)
            container.remove()
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"Container {identifier} not found")
        except Exception as e:
            raise RuntimeError(f"Failed to remove container: {str(e)}")

    def run_command(self, identifier, command, service=None):
        try:
            if service:
                result = subprocess.run(
                    ["docker", "compose", "-f", identifier, "exec", service]
                    + command.split(),
                    capture_output=True,
                    text=True,
                )
            else:
                container = self.get_container(identifier)
                result = container.exec_run(command)
                return result.output.decode()
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"Container {identifier} not found")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run command in service: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to run command: {str(e)}")
        return result.stdout

    def create_volume(self, name):
        try:
            volume = self.client.volumes.create(name)
            return volume
        except Exception as e:
            raise RuntimeError(f"Failed to create volume: {str(e)}")

    def remove_volume(self, name):
        try:
            volume = self.client.volumes.get(name)
            volume.remove()
        except docker.errors.NotFound:
            raise docker.errors.NotFound(f"Volume {name} not found")
        except Exception as e:
            raise RuntimeError(f"Failed to remove volume: {str(e)}")

    def read_compose_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Docker Compose file {file_path} not found")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse Docker Compose file: {str(e)}")

    def write_compose_file(self, file_path, data):
        try:
            with open(file_path, "w") as file:
                yaml.safe_dump(data, file)
        except Exception as e:
            raise RuntimeError(f"Failed to write Docker Compose file: {str(e)}")

    def start_compose_services(self, file_path, services=None):
        try:
            if services:
                services_to_start = self.get_service_dependencies(file_path, services)
                subprocess.run(
                    ["docker", "compose", "-f", file_path, "up", "-d"]
                    + services_to_start,
                    check=True,
                )
            else:
                subprocess.run(
                    ["docker", "compose", "-f", file_path, "up", "-d"], check=True
                )
        except subprocess.CalledProcessError:
            raise RuntimeError(
                f"Failed to start services using Docker Compose file {file_path}"
            )

    def stop_compose_services(self, file_path):
        try:
            subprocess.run(["docker", "compose", "-f", file_path, "down"], check=True)
        except subprocess.CalledProcessError:
            raise RuntimeError(
                f"Failed to stop services using Docker Compose file {file_path}"
            )

    def update_volumes_in_compose(self, file_path, service_name, volume_mappings):
        try:
            compose_data = self.read_compose_file(file_path)

            if "services" in compose_data and service_name in compose_data["services"]:
                service = compose_data["services"][service_name]
                updated_volumes = []
                for volume in service.get("volumes", []):
                    src, _, dest = volume.partition(":")
                    if src in volume_mappings:
                        updated_volumes.append(f"{volume_mappings[src]}:{dest}")
                    else:
                        updated_volumes.append(volume)
                service["volumes"] = updated_volumes

            self.write_compose_file(file_path, compose_data)
        except Exception as e:
            raise RuntimeError(
                f"Failed to update volumes in Docker Compose file: {str(e)}"
            )

    def create_dev_container(self, name, image, volumes=None):
        config = {
            "type": "container",
            "name": name,
            "image": image,
            "volumes": volumes or [],
        }
        self.config_manager.create_config(name, config)
        return self.create_container(image, name, volumes)

    def remove_dev_container(self, name):
        self.config_manager.delete_config(name)
        self.remove_container(name)

    def remove_dev_compose(self, name):
        config = self.config_manager.read_config(name)
        self.config_manager.delete_config(name)
        self.stop_compose_services(config["compose_file"])

    def activate_dev(self, name, services=None):
        config = self.config_manager.read_config(name)
        if config["type"] == "container":
            self.start_container(config["name"])
        elif config["type"] == "compose":
            if services:
                self.start_compose_services(config["compose_file"], services)
            else:
                self.start_compose_services(config["compose_file"])
        return config

    def load_external_config(self, file_path):
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"External configuration file {file_path} not found"
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Failed to parse external configuration file: {str(e)}"
            )

    def get_service_dependencies(self, file_path, services):
        compose_data = self.read_compose_file(file_path)
        all_services_to_start = set(services)
        for service in services:
            all_services_to_start.update(
                self._get_dependencies_recursive(compose_data, service)
            )
        return list(all_services_to_start)

    def _get_dependencies_recursive(self, compose_data, service):
        dependencies = set()
        if "depends_on" in compose_data["services"].get(service, {}):
            for dependency in compose_data["services"][service]["depends_on"]:
                dependencies.add(dependency)
                dependencies.update(
                    self._get_dependencies_recursive(compose_data, dependency)
                )
        return dependencies
