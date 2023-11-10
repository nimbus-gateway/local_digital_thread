import os
import docker
import dockerpty
import compose

def restart_service(service_name, compose_file):
    # Change the working directory to the location of the docker-compose.yml file
    compose_dir = os.path.dirname(compose_file)
    os.chdir(compose_dir)

    # Initialize the Docker Compose client
    client = docker.from_env()
    project = compose.project.from_config(
        project_dir=compose_dir,
        config_files=[compose_file]
    )

    # Restart the specified service
    service = project.get_service(service_name)
    service.ensure_image_exists()
    service.recreate()

    # Print a message
    print(f"Service {service_name} has been restarted.")

if __name__ == "__main__":
    compose_file = 'path/to/your/docker-compose.yml'
    service_name = 'your_service_name'

    restart_service(service_name, compose_file)