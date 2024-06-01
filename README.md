# DevDock

DevDock is a Python library and CLI tool for managing development containers. It supports Docker images and Docker Compose configurations, allowing for easy container creation, volume management, and service orchestration.

## Features
- Create and manage Docker containers with multiple volume mappings.
- Create and manage Docker Compose configurations with service dependencies.
- Activate specific services along with their dependencies.
- Run commands and open shells inside specific services.

## Installation

Install DevDock using pip:

```bash
pip install devdock
```

## Usage

### Create a Container from an Image

```bash
devdock mkdevcontainer --image python:3.9 --name my-python-container --volumes /host/path1:/container/path1,/host/path2:/container/path2
```

### Run Services from a Docker Compose File with Volume Mappings

```bash
devdock mkdevcontainer -f docker-compose.yaml --name my-compose --volume-mappings web:/host/path1:/var/www,web:/host/path2:/var/log/nginx,redis:/host/redis1:/data,db:/host/db1:/var/lib/postgresql/data
```

### Activate a Configuration

```bash
devdock workon my-compose
```

### Activate Specific Services in a Compose Configuration

```bash
devdock workon my-compose --services web
```

### Remove a Configuration

```bash
devdock rmdev my-compose
```

### Stop a Container

```bash
devdock stop my-python-container
```

### Remove a Container

```bash
devdock remove my-python-container
```

### Run a Command Inside a Specific Service

```bash
devdock run my-compose --service web "echo Hello, World!"
```

### Enter Shell Inside a Specific Service

```bash
devdock shell my-compose --service web
```

## Example Docker Compose File

Here's a sample `docker-compose.yaml` file for reference:

```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    depends_on:
      - redis
    volumes:
      - web_data:/var/www
      - web_logs:/var/log/nginx

  redis:
    image: redis:latest
    depends_on:
      - db
    volumes:
      - redis_data:/data

  db:
    image: postgres:latest
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  web_data:
  web_logs:
  redis_data:
  db_data:
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write your code and tests.
4. Run the tests to make sure everything is working.
5. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or need further assistance, please feel free to reach out to the project maintainer:

**Ali Tavallaie**
- Email: a.tavallaie@gmail.com
