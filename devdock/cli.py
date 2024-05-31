import click
from devdock.manager import DevContainerManager
from devdock.shell import run_shell, run_command
import docker
import yaml


@click.group()
def cli():
    pass


@cli.command()
@click.option("--image", prompt="Docker image", help="The Docker image to use")
@click.option("--name", prompt="Container name", help="The name of the container")
@click.option(
    "--volumes", multiple=True, help="Volume mappings (host_path:container_path)"
)
def mkdevcontainer(image, name, volumes):
    manager = DevContainerManager()
    try:
        container = manager.create_dev_container(name, image, volumes)
        click.echo(f"Dev container {container.name} created with ID {container.id}.")
    except docker.errors.ImageNotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option(
    "--compose-file",
    prompt="Docker Compose file path",
    help="The path to the Docker Compose file",
)
@click.option(
    "--name", prompt="Configuration name", help="The name of the configuration"
)
def mkdevcompose(compose_file, name):
    manager = DevContainerManager()
    try:
        manager.create_dev_compose(name, compose_file)
        click.echo(f"Dev compose configuration {name} created and services started.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("name")
def rmdev(name):
    manager = DevContainerManager()
    try:
        config = manager.config_manager.read_config(name)
        if config["type"] == "container":
            manager.remove_dev_container(name)
        elif config["type"] == "compose":
            manager.remove_dev_compose(name)
        click.echo(f"Dev configuration {name} removed.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("name")
def workon(name):
    manager = DevContainerManager()
    try:
        config = manager.activate_dev(name)
        click.echo(f'Activated dev configuration {config["name"]}.')
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
def start(identifier):
    manager = DevContainerManager()
    try:
        manager.start_container(identifier)
        click.echo(f"Container {identifier} started.")
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
def stop(identifier):
    manager = DevContainerManager()
    try:
        manager.stop_container(identifier)
        click.echo(f"Container {identifier} stopped.")
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
def remove(identifier):
    manager = DevContainerManager()
    try:
        manager.remove_container(identifier)
        click.echo(f"Container {identifier} removed.")
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
@click.argument("command")
def run(identifier, command):
    manager = DevContainerManager()
    try:
        result = manager.run_command(identifier, command)
        click.echo(result.output.decode())
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
def shell(identifier):
    try:
        run_shell(identifier)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option("--name", prompt="Volume name", help="The name of the volume")
def create_volume(name):
    manager = DevContainerManager()
    try:
        volume = manager.create_volume(name)
        click.echo(f"Volume {volume.name} created.")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option("--name", prompt="Volume name", help="The name of the volume")
def remove_volume(name):
    manager = DevContainerManager()
    try:
        manager.remove_volume(name)
        click.echo(f"Volume {name} removed.")
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option(
    "--file_path",
    prompt="Compose file path",
    help="The path to the Docker Compose file",
)
def start_compose(file_path):
    manager = DevContainerManager()
    try:
        manager.start_compose_services(file_path)
        click.echo(f"Services in {file_path} started.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except RuntimeError as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option(
    "--file_path",
    prompt="Compose file path",
    help="The path to the Docker Compose file",
)
def stop_compose(file_path):
    manager = DevContainerManager()
    try:
        manager.stop_compose_services(file_path)
        click.echo(f"Services in {file_path} stopped.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except RuntimeError as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option(
    "--file_path",
    prompt="Compose file path",
    help="The path to the Docker Compose file",
)
@click.option(
    "--volume_mappings",
    prompt="Volume mappings (e.g., old_volume1=new_volume1,old_volume2=new_volume2)",
    help="Volume mappings to update",
)
def update_volumes(file_path, volume_mappings):
    manager = DevContainerManager()
    try:
        volume_mappings = dict(
            mapping.split("=") for mapping in volume_mappings.split(",")
        )
        manager.update_volumes_in_compose(file_path, volume_mappings)
        click.echo(f"Volumes in {file_path} updated.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.option(
    "-f",
    "--config-file",
    type=click.Path(exists=True),
    help="Path to an external config file",
)
def load_config(config_file):
    manager = DevContainerManager()
    try:
        config = manager.load_external_config(config_file)
        name = config.get("name")
        if config["type"] == "container":
            manager.create_dev_container(name, config["image"], config.get("volumes"))
        elif config["type"] == "compose":
            manager.create_dev_compose(name, config["compose_file"])
        click.echo(f"Loaded configuration from {config_file} and started {name}.")
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}")
    except yaml.YAMLError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
