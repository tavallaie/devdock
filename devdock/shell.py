import subprocess
import click


def run_shell(container_id):
    try:
        command = f"docker exec -it {container_id} /bin/bash"
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to run shell in container {container_id}: {str(e)}")


def run_command(container_id, command):
    try:
        cmd = f"docker exec -it {container_id} {command}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(
            f"Failed to run command '{command}' in container {container_id}: {str(e)}"
        )
