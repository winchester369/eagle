import json

from db import ger_servers_from_db, get_last_system_info_by_server_id

from flask import Flask, render_template

app = Flask("MONITOR_ROOM")


def render_system_info_as_html_page():
    return render_template('dashboard.html')


@app.route('/api/system_infos')
def api_system_infos():
    servers = ger_servers_from_db()
    servers_system_infos = []
    for server in servers:
        system_info = get_last_system_info_by_server_id(server_id=server['id'])
        print(system_info)
        # system_info=json.loads(system_info['json_data'])
        # system_info['id']=server['id']
        system_info['code'] = server['code']
        # system_info['username']=server['username']
        servers_system_infos.append(system_info)
    return json.dumps(servers_system_infos)


@app.route('/')
def index():
    return render_system_info_as_html_page()


if __name__ == "__main__":
    app.run(debug=False)
