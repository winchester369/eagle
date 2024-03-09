import threading
from datetime import  datetime
from time import sleep

from db import ger_servers_from_db, set_access_token, store_system_info
from api import get_token, get_system_info


def get_and_update_access_token(server):
    access_token = get_token(username=server['username'], password=server['password'], base_url=server['base_url'])
    set_access_token(server_id=server['id'], access_token=access_token)
    if env == 'dev':
        print(f"Server {server['id']}: {access_token} updated")
    return access_token

def get_servers_access_token():
    result = list()
    servers = ger_servers_from_db()
    for server in servers:
        if server['access_token'] is None:
            access_token = get_and_update_access_token(server)
        else:
            access_token = server['access_token']
            # if env == 'dev':
                # print(f"Server {server['id']}: {server['access_token']} fetched")
        result.append({
            'id': server['id'],
            'username': server['username'],
            'password': server['password'],
            'access_token': access_token,
            'base_url': server['base_url']
        })

    return result


def update_system_info(ser):
    sleep(3)
    if env == 'dev':
        print(f"Get info for Server {ser['id']}")

    server_info = get_system_info(ser['base_url'], ser['access_token'])
    if server_info is None:
        ser['access_token'] = get_and_update_access_token(ser)
        return update_system_info(ser)

    store_system_info(ser['id'], server_info)
    my_thread = threading.Thread(target=update_system_info, args=(ser,))
    my_thread.start()

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    env = 'dev'
    # env = 'prod'
    server_tokens = get_servers_access_token()

    for server in server_tokens:
        my_thread = threading.Thread(target=update_system_info, args=(server,))
        my_thread.start()
        # update_system_info(server)
        print(f"Update System Info at", get_current_time())
    # while True:
    #     update_system_info()
    #     sleep(5)
