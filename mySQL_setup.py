"""
Setup MySQL container using Docker SDK
"""
import time

import docker
import mysql.connector
from mysql.connector import Error


# Run the MySQL container using the Docker SDK
def run_mysql_container():
    client = docker.from_env()

    print ("Starting MySQL container")
    
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
        print(
            f"Starting existing MySQL container with ID: {mysql_container.id}")
        mysql_container.start()
    else:
        # Environment variables for the MySQL container
        env_vars = {
            "MYSQL_ROOT_PASSWORD": "my-secret-pw",
            "MYSQL_DATABASE": "mydatabase",
            "MYSQL_USER": "myuser",
            "MYSQL_PASSWORD": "mypassword"
        }

        # Run the MySQL container
        container = client.containers.run(
            "mysql:latest",
            name="my-mysql",
            environment=env_vars,
            ports={'3306/tcp': 3306},
            detach=True
        )

        print(f"Running new MySQL container with ID: {container.id}")

# Example usage - for testing
# run_mysql_container()

# Create mySQL tables


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
            Crypto_Code VARCHAR(10),
            value DECIMAL(10, 2),
            date DATE,
            UNIQUE (Crypto_Code, date)
        )
    """)
    # Table creation for 'crypto_news'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Crypto_Code VARCHAR(10),
            ID_News INT,
            Kind VARCHAR(10),
            Title VARCHAR(1000),
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
            sentiment VARCHAR(20),
            Domain VARCHAR(100),
            UNIQUE (ID_News, Crypto_Code)
        )
    """)

    # Table creation for 'HQ_newagency'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HQ_newagency (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Domain VARCHAR(100) UNIQUE,
            hq_location VARCHAR(100),
            latitude DECIMAL(12, 8) NULL,
            longitude DECIMAL(12, 8) NULL
        )
    """)

    cursor.close()
    db.close()
    print("MySQL tables created successfully.")

# Example usage - for testing
#create_mysql_tables()

# Wait for the MySQL container to be ready to accept connections
# Sometimes the creation of the MySQL container takes a while. This function waits for the container to be ready to accept connections.


def wait_for_mysql_container_ready(host, user, password, database, max_attempts=10, delay=5):
    """Wait for the MySQL container to be ready to accept connections."""
    attempt = 0
    while attempt < max_attempts:
        try:
            connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database)
            if connection.is_connected():
                print("MySQL container is ready to accept connections.")
                connection.close()
                return True
        except Error:
            print(
                f"Waiting for MySQL container to be ready. Attempt {attempt + 1}/{max_attempts}...")
            attempt += 1
            time.sleep(delay)
    print("MySQL container did not become ready in time.")
    return False
