import mysql.connector

import mysql.connector

# Connect to the database
db_connection = mysql.connector.connect(
    host="localhost",
    port="8888",
    user="jackie",
    password="jackie_password",
    database="ai_generated_text"
)


def insert(input_data):
    # Create a cursor object
    cursor = db_connection.cursor()

    # SQL query to insert a record
    sql = "INSERT INTO monitor_data (id, text_hash, model_type, count_ai, count_human) VALUES (%s, %s, %s, %s, %s)"
    val = tuple(input_data)

    # Execute the query
    cursor.execute(sql, val)

    # Commit to the database
    db_connection.commit()

    # Close the cursor and connection
    cursor.close()
    db_connection.close()
    print(cursor.rowcount, "record inserted.")


if __name__ == '__main__':
    input_data = [1, 'abcdef', 'standard', 10, 11]
    insert(input_data)
