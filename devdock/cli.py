import click
from devdock.manager import DevContainerManager
from devdock.shell import run_shell
import docker
import subprocess


@click.group()
def cli():
    pass


@cli.command()
@click.option("--image", help="The Docker image to use")
@click.option("--name", prompt="Container name", help="The name of the container")
@click.option(
    "--volumes", multiple=True, help="Volume mappings (host_path:container_path)"
)
@click.option(
    "-f", "--compose-file", type=click.Path(), help="Path to the Docker Compose file"
)
@click.option(
    "--volume-mappings",
    multiple=True,
    help="Volume mappings for services (service_name:host_path:container_path)",
)
def mkdevcontainer(image, name, volumes, compose_file, volume_mappings):
    manager = DevContainerManager()
    try:
        if compose_file:
            manager.create_dev_compose(name, compose_file, volume_mappings)
            click.echo(
                f"Dev compose configuration {name} created and services started."
            )
        else:
            volume_list = [v for v in volumes]
            container = manager.create_dev_container(name, image, volume_list)
            click.echo(
                f"Dev container {container.name} created with ID {container.id}."
            )
    except docker.errors.ImageNotFound as e:
        click.echo(f"Error: {str(e)}")
    except ValueError as e:
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
@click.option("--services", multiple=True, help="The specific services to activate")
def workon(name, services):
    manager = DevContainerManager()
    try:
        config = manager.activate_dev(name, services)
        if services:
            click.echo(
                f'Activated dev configuration {config["name"]} for services {", ".join(services)}.'
            )
        else:
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
@click.option("--service", help="The specific service to run the command in")
def run(identifier, command, service):
    manager = DevContainerManager()
    try:
        output = manager.run_command(identifier, command, service)
        click.echo(output)
    except docker.errors.NotFound as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.command()
@click.argument("identifier")
@click.option("--service", help="The specific service to run the shell in")
def shell(identifier, service):
    manager = DevContainerManager()
    try:
        if service:
            result = subprocess.run(
                ["docker", "compose", "-f", identifier, "exec", service, "/bin/bash"],
                check=True,
            )
            click.echo(result.stdout)
        else:
            run_shell(identifier)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
