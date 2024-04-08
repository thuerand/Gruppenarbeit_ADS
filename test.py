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
            # Assuming "19337058" is the ID and stored in a column named 'ID'
            query = "SELECT * FROM crypto_news WHERE ID_news = %s AND Crypto_Code = %s"
            cursor.execute(query, ('19337058','USDT'))
            
            # Fetch the result
            record = cursor.fetchall()
            
            if record:
                print("Found record:", record)
            else:
                print("Record not found.")
                
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
