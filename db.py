import json
import sqlite3


def ger_servers_from_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM server')
    server = cursor.fetchall()
    conn.close()
    servers = [{
        "id": server[0],
        "code": server[1],
        "username": server[2],
        "password": server[3],
        "access_token": server[4],
        "base_url": server[5],
    } for server in server]
    return servers


def set_access_token(server_id, access_token):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('UPDATE server SET access_token = ? WHERE id = ?', (access_token, server_id))
    conn.commit()
    conn.close()


def store_system_info(server_id, system_info):
    # system_info = json.dumps(system_info)
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO system_info (server_id, json_data) VALUES (?, ?)', (server_id, system_info))
    conn.commit()
    conn.close()


def get_last_system_info_by_server_id(server_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_info WHERE server_id = ? ORDER BY id DESC LIMIT 1', (server_id,))
    system_info = cursor.fetchone()
    # print(system_info)
    # system_info = system_info[0]
    print(server_id)
    json_data = json.loads(system_info[2])
    # print(system_info[0])
    conn.close()
    return {
        'id': system_info[0],
        'server_id': system_info[1],
        'json_data': json_data,
        'created_at': system_info[3],
        'updated_at': system_info[4],
    }
