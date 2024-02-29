import json
import sqlite3

DB_FILE = 'db.sqlite3'


def execute_query(query, parameters=None):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor


def ger_servers_from_db():
    query = 'SELECT * FROM server'
    cursor = execute_query(query)

    servers = [{
        "id": server[0],
        "code": server[1],
        "username": server[2],
        "password": server[3],
        "access_token": server[4],
        "base_url": server[5],
    } for server in cursor.fetchall()]

    return servers


def set_access_token(server_id, access_token):
    query = 'UPDATE server SET access_token = ? WHERE id = ?'
    parameters = (access_token, server_id)
    execute_query(query, parameters)


def store_system_info(server_id, system_info):
    query = 'INSERT INTO system_info (server_id, json_data) VALUES (?, ?)'
    parameters = (server_id, system_info)
    execute_query(query, parameters)


def get_last_system_info_by_server_id(server_id):
    query = 'SELECT * FROM system_info WHERE server_id = ? ORDER BY id DESC LIMIT 1'
    parameters = (server_id,)
    cursor = execute_query(query, parameters)

    system_info = cursor.fetchone()

    if system_info:
        json_data = json.loads(system_info[2])
        return {
            'id': system_info[0],
            'server_id': system_info[1],
            'json_data': json_data,
            'created_at': system_info[3],
            'updated_at': system_info[4],
        }
    else:
        return None


def get_last_system_info_chart_data(server):
    query = 'SELECT created_at, json_data FROM system_info WHERE server_id = ? ORDER BY created_at LIMIT 10000'
    parameters = (server['id'],)
    cursor = execute_query(query, parameters)

    chart_data_list = []

    for record in cursor.fetchall():
        try:
            created_at = record[0]
            json_data = json.loads(record[1])
            # Assuming json_data structure includes online_users as a list
            online_users = json_data.get('online_users_f_1_m', 0)
            outgoing_bandwidth_speed = json_data.get('outgoing_bandwidth_speed', 0)
            incoming_bandwidth_speed = json_data.get('incoming_bandwidth_speed', 0)
            incoming_bandwidth = json_data.get('incoming_bandwidth', 0)
            outgoing_bandwidth = json_data.get('outgoing_bandwidth', 0)
            chart_data = {
                'code': server['code'],
                'created_at': created_at,
                'online_user_count': online_users,
                'total_speed': outgoing_bandwidth_speed+incoming_bandwidth_speed,
                'total_used_traffic': incoming_bandwidth+outgoing_bandwidth,
            }

            chart_data_list.append(chart_data)
        except Exception as e:
            print(f'Error parsing JSON data: {e}')
            continue

    return chart_data_list
