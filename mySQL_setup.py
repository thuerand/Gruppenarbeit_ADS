# Setup MySQL container using Docker SDK

import docker
import mysql.connector
import pandas as pd

# Run the MySQL container using the Docker SDK
def run_mysql_container():
    client = docker.from_env()

    # Check if the MySQL container is already running
    containers = client.containers.list(all=True)
    mysql_container = None
    for container in containers:
        if container.name == "my-mysql":
            mysql_container = container
            break

    if mysql_container and mysql_container.status == "running":
        print(f"Found running MySQL container with ID: {mysql_container.id}")
    elif mysql_container and mysql_container.status == "exited":
        # If the container exists but is not running, start it
        print(f"Starting existing MySQL container with ID: {mysql_container.id}")
        mysql_container.start()
    else:
        # Environment variables for the MySQL container
        env_vars = {
            "MYSQL_ROOT_PASSWORD": "my-secret-pw",
            "MYSQL_DATABASE": "mydatabase",
            "MYSQL_USER": "myuser",
            "MYSQL_PASSWORD": "mypassword"
        }

        # Pull the MySQL image
        image = client.images.pull("mysql:latest")
        print(f"Pulled {image.tags[0]} successfully.")

        # Run the MySQL container
        container = client.containers.run(
            "mysql:latest",
            name="my-mysql",
            environment=env_vars,
            ports={'3306/tcp': 3306},
            detach=True
        )

        print(f"Running new MySQL container with ID: {container.id}")

run_mysql_container()

# Sometimes the creation of the MySQL container takes a while. This function waits for the container to be ready to accept connections.
def wait_for_mysql_container_ready(host, user, password, database, max_attempts=10, delay=5):
    """Wait for the MySQL container to be ready to accept connections."""
    attempt = 0
    while attempt < max_attempts:
        try:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            if connection.is_connected():
                print("MySQL container is ready to accept connections.")
                connection.close()
                return True
        except Error as e:
            print(f"Waiting for MySQL container to be ready: {e}")
            attempt += 1
            time.sleep(delay)
    print("MySQL container did not become ready in time.")
    return False

# Import the data from csv-files to the MySQL container
def create_mysql_tables():
    db = mysql.connector.connect(
        host="localhost",
        user="myuser",
        password="mypassword",
        database="mydatabase"
    )
    cursor = db.cursor()

    # Table creation for 'daily_data'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            value DECIMAL(10, 2),
            date DATE,
            crypto_id VARCHAR(10)
        )
    """)
    # Table creation for 'crypto_news'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            crypto_id VARCHAR(10),
            ID_Cryptopanic INT,
            Kind VARCHAR(10),
            Positive_Votes INT,
            Negative_Votes INT,
            Important_Votes INT,
            Liked_Votes INT,
            Disliked_Votes INT,
            LOL_Votes INT,
            Toxic_Votes INT,
            Saved INT,
            Comments INT,
            published_at DATETIME,
            Domain VARCHAR(100)
        )
    """)

    # Table creation for 'HQ_newagency'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HQ_newagency (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Domain VARCHAR(100),
            hq_location VARCHAR(100)
        )
    """)

    cursor.close()
    db.close()

create_mysql_tables()