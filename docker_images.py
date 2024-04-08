# Installing various Docker images using the Docker SDK

# Note:
# - You could start ChromeDriver via Docker as well but the Version has to fit with Chrome and therefore you have to install chrome too.. it's not worth it.

import docker

def run_install_Docker_images():
    # Create a Docker client
    print("Installing Docker images...")
    client = docker.from_env()

    # Pull the latest MySQL image
    image = client.images.pull("mysql:latest")

    print(f"Pulled {image.tags[0]} successfully.")

run_install_Docker_images()