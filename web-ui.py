import json

from db import ger_servers_from_db, get_last_system_info_by_server_id,get_last_system_info_chart_data

from flask import Flask, render_template, jsonify

app = Flask("MONITOR_ROOM")


def render_system_info_as_html_page():
    return render_template('dashboard.html')


@app.route('/api/system_infos')
def api_system_infos():
    servers = ger_servers_from_db()
    try:
        servers_system_infos = []
        for server in servers:
            system_info = get_last_system_info_by_server_id(server_id=server['id'])
            # print(system_info)
            # system_info=json.loads(system_info['json_data'])
            system_info['id'] = server['id']
            system_info['code'] = server['code']
            # system_info['username']=server['username']
            servers_system_infos.append(system_info)

        return jsonify(servers_system_infos)
        # return jsonify(servers_system_infos)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system_charts')
def api_system_charts():
    try:
        servers = ger_servers_from_db()
        all_servers_chart_data = {}

        for server in servers:
            chart_data = get_last_system_info_chart_data(server=server)
            # chart_data['code'] = server['code']
            all_servers_chart_data[server['id']] = chart_data

        return jsonify(all_servers_chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return render_system_info_as_html_page()


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
