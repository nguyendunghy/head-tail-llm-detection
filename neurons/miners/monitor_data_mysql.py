import time
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import bittensor as bt
import mysql.connector

global_tunnel = None
global_db_connection = None


def get_db_connection(ip, port):
    global global_db_connection
    if global_db_connection is not None and global_db_connection.is_connected():
        return global_db_connection

    global_db_connection = mysql.connector.connect(
        host=str(ip),
        port=str(port),  # 8888
        user="jackie",
        password="jackie_password",
        database="ai_generated_text"
    )
    return global_db_connection


def check_exists(db_connection, input_list):
    cursor = db_connection.cursor()
    list_sql = []
    for i in range(len(input_list)):
        input = input_list[i]
        head_db = input[0]
        head_hash = input[1]
        tail_db = input[2]
        tail_hash = input[3]
        tmp_sql = "(select {} as pos,hash FROM table_{} where hash = '{}' limt 1) " \
                  "union (select {} as pos,hash FROM table_{} where hash = '{}' limit 1) " \
            .format(str(i), str(head_db), str(head_hash), str(i), str(tail_db), str(tail_hash))
        list_sql.append(tmp_sql)
    sql = ' union '.join(list_sql)
    bt.logging.info("query sql: " + sql)
    cursor.execute(sql)
    result = [False for _ in range(len(input_list))]
    for row in cursor.fetchall():
        ind = int(row[0])
        result[ind] = True

    cursor.close()
    return result

def get_tunnel():
    global global_tunnel
    if global_tunnel is not None:
        return global_tunnel

    global_tunnel = SSHTunnelForwarder(('70.48.87.64', 41264),
                                       ssh_username='root',
                                       ssh_private_key='./fluidstack',
                                       remote_bind_address=('localhost', 8888),
                                       local_bind_address=('localhost', 7106)
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
    ip = get_tunnel().local_bind_host
    print("tunnel ip: " + str(ip))
    print("tunnel port: " + str(port))
    conn = get_db_connection(ip, port)
    print("create conn success")
    insert(conn, input_data)


if __name__ == '__main__':
    for i in range(5):
        start_time = time.time_ns()
        input_data = [start_time // 1_000_000, 'abcdef', 'standard', 10, 11]
        tunnel_insert(input_data)
        end_time = time.time_ns()
        print("time processing ", str(end_time - start_time))
