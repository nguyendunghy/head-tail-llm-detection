import time
import mysql.connector
from sshtunnel import SSHTunnelForwarder

import mysql.connector

global_tunnel = None
global_db_connection = None


def get_db_connection(port):
    global global_db_connection
    if global_db_connection != None:
        return global_db_connection

    global_db_connection = mysql.connector.connect(
        host="localhost",
        port=port,  # 8888
        user="jackie",
        password="jackie_password",
        database="ai_generated_text"
    )
    return global_db_connection


def get_tunnel():
    global global_tunnel
    if global_tunnel != None:
        return global_tunnel

    global_tunnel = SSHTunnelForwarder(('70.48.87.64', 41264),
                                       ssh_username='root',
                                       ssh_private_key='./fluidstack',
                                       remote_bind_address=('localhost', 8888),
                                       local_bind_address=('localhost', 7101)#148.77.2.74:42820 -> 7101/tcp
                                       )
    global_tunnel.start()
    return global_tunnel


def insert(db_connection, input_data):
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
    # db_connection.close()
    print(cursor.rowcount, "record inserted.")


def tunnel_insert(input_data):
    port = get_tunnel().local_bind_port
    print("tunnel port: " + str(port))
    conn = get_db_connection(port)
    insert(conn, input_data)


if __name__ == '__main__':
    for i in range(5):
        start_time = time.time_ns()
        input_data = [start_time // 1_000_000, 'abcdef', 'standard', 10, 11]
        tunnel_insert(input_data)
        end_time = time.time_ns()
        print("time processing ", str(end_time - start_time))
