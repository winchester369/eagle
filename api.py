import time

import requests

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}


def get_token(username, password, base_url):
    time.sleep(1)
    data = {
        'grant_type': '',
        'username': username,
        'password': password,
        'scope': '',
        'client_id': '',
        'client_secret': '',
    }
    try:
        response = requests.post('%s/admin/token' % base_url, headers=headers, data=data, timeout=3)
        if response.status_code != 200:
            print("got:", response.status_code)
            return get_token(username, password, base_url)
        access_token = response.json()['access_token']
    except Exception as e:
        print("exeption get_token:", base_url)
        return get_token(username, password, base_url)
    return access_token


def get_system_info(base_url, access_token):
    time.sleep(1)
    head = headers.copy()
    head['Authorization'] = 'Bearer %s' % access_token
    try:
        response = requests.get('%s/system' % base_url, headers=head, timeout=3)
    except Exception as e:
        print("exeption get_system_info:", base_url,e)
        # print(response.status_code)
        return get_system_info(base_url, access_token)
    # response = requests.get('%s/system' % base_url, headers=head)
    if response.status_code != 200:
        print("got:", response.status_code)
        return get_system_info(base_url, access_token)
    data = response.text
    return data
