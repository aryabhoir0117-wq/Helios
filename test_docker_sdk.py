import docker

client = docker.from_env()

for container in client.containers.list():
    print(container.name, container.status, container.id[:12])