import mysql.connector
from mysql.connector import Error

def get_news_record():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(host='localhost',
                                             database='mydatabase',
                                             user='myuser',
                                             password='mypassword')
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Define the SELECT statement query
            query = "SELECT * FROM hourly_data;"
            cursor.execute(query)
            
            # Fetch the results
            records = cursor.fetchall()
            
            if records:
                print("Found records:")
                for record in records:
                    print(record)
            else:
                print("No records found.")
                
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

# Example usage
get_news_record()
