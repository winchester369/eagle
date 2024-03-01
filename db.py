import json
import sqlite3
from datetime import datetime, timedelta
import random

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


def get_last_system_info_chart_data():
    ten_days_ago = datetime.now() - timedelta(days=3)

    query = f"SELECT server_id,created_at, json_data FROM system_info WHERE created_at >= '{ten_days_ago.strftime('%Y-%m-%d %H:%M:%S')}'"
    # parameters = (server['id'],)

    sql_query = """
        SELECT info.server_id, info.created_at, info.json_data, ser.code
        FROM (
            SELECT info.server_id, info.created_at, info.json_data, ser.code,
                   ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m-%d %H', created_at) ORDER BY created_at DESC) as info.row_num
            FROM system_info info""" + f" WHERE info.created_at >= '{ten_days_ago.strftime('%Y-%m-%d %H:%M:%S')}' " + """
            JOIN server ser ON info.server_id = ser.id
        ) AS ranked
        WHERE info.row_num <= 1000
        ORDER BY info.created_at ASC;
    """
    sql = """
        EXPLAIN SELECT server_id, created_at, json_data
        FROM (
            SELECT server_id, created_at, json_data,
                   ROW_NUMBER() OVER (PARTITION BY strftime('%Y-%m-%d', created_at) ORDER BY created_at DESC) as row_num
            FROM system_info
        ) AS ranked
        WHERE row_num <= 24
        ORDER BY created_at DESC;
    """
    sql_query = """
        SELECT system_info.server_id, system_info.created_at, system_info.json_data, server.code
        FROM system_info
        JOIN server ON system_info.server_id = server.id
        WHERE strftime('%M', system_info.created_at) = '01'
        AND system_info.created_at >= (SELECT MAX(created_at) FROM system_info) - 3*24*3600  -- Last 3 days
        ORDER BY system_info.created_at ASC ;
    """
    cursor = execute_query(sql_query)

    labels = []
    chart_data_list = []

    server_infos = {}

    # Prepare data for Chart.js
    chart_data = {
        'labels': [],  # common labels for x-axis (created_at)
        'datasets': []
    }

    # Define a set of distinct colors
    colors = ['#FF5733', '#33FF57', '#5733FF', '#FF3366', '#33FFFF', '#FFFF33', '#3366FF', '#FF33FF']

    for index,record in enumerate(cursor.fetchall()):
        try:
            server_id, created_at, json_data, server_code = record

            json_data = json.loads(json_data)
            # Assuming json_data structure includes online_users as a list
            online_users = json_data.get('online_users_f_1_m', 0)
            outgoing_bandwidth_speed = json_data.get('outgoing_bandwidth_speed', 0)
            incoming_bandwidth_speed = json_data.get('incoming_bandwidth_speed', 0)
            incoming_bandwidth = json_data.get('incoming_bandwidth', 0)
            outgoing_bandwidth = json_data.get('outgoing_bandwidth', 0)

            # chart_data = {
            #     'code': server_code,
            #     'created_at': created_at,
            #     'online_user_count': online_users,
            #     'total_speed': outgoing_bandwidth_speed + incoming_bandwidth_speed,
            #     'total_used_traffic': incoming_bandwidth + outgoing_bandwidth,
            # }
            #
            # chart_data['labels'].append(created_at)
            #
            # dataset = {
            #     'label': f'{server_code}',
            #     'data': [online_users],
            #     'fill': False,
            #     'borderColor': colors[index % len(colors)],  # Use a color from the list, cycling if necessary
            #     'lineTension': 0.1
            # }
            # chart_data['datasets'].append(dataset)

            if server_id not in server_infos:
                server_infos[server_id] = {'labels': [], 'data': [],'code':server_id}

            server_infos[server_id]['labels'].append(created_at)
            server_infos[server_id]['code']=server_code
            server_infos[server_id]['data'].append(online_users)
            #
            # labels.append(created_at)
            # chart_data_list.append(chart_data)
        except Exception as e:
            print(f'Error parsing JSON data: {e}')
            continue

    # return chart_data


    for index, data in server_infos.items():
        chart_data['labels'] = data['labels']  # Assume all servers have the same timestamps

        dataset = {
            'label': f"{data['code']}",
            'data': data['data'],
            'fill': False,
            'borderColor': colors[index % len(colors)],  # Use a color from the list, cycling if necessary
            'lineTension': 0.1
        }

        chart_data['datasets'].append(dataset)
    chart_data_json = json.dumps(chart_data)
    print(chart_data_json)
    return chart_data
