import string
import random
from datetime import datetime, timedelta
from time import time
from pprint import pprint
import argparse

import requests

_candidates = string.ascii_lowercase + string.digits


def generate_logs(n, date_len, key, value):
    basetime = int(time())
    now = datetime.fromtimestamp(basetime)
    return [
        {
            key: value,
            'created': datetime.strftime(now + timedelta(seconds=i), '%Y-%m-%dT%H:%M:%S'),
            'data': ''.join(random.choices(_candidates, k=date_len)),
            'timestamp': basetime + i,
        } for i in range(n)
    ]


def post_logs(group_name, logs, host='localhost', port=8080):
    if not isinstance(logs, list):
        raise TypeError(f'logs should be list: {repr(logs)}')
    for log in logs:
        if not isinstance(log, dict):
            raise TypeError(f'log should be dict: {repr(log)}')

    url = f'http://{host}:{port}/groups/{group_name}'
    resp = requests.post(url=url, json=logs)
    return resp.status_code, resp.json()


def get_key_value_matched_logs(group_name, key, value, host='localhost', port=8080):
    url = f'http://{host}:{port}/groups/{group_name}?{key}={value}'
    resp = requests.get(url=url)
    return resp.status_code, resp.json()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser(description='Test post and get with sample logs.')

    server_group = parser.add_argument_group('log server')
    server_group.add_argument('-s', dest='host', type=str, default='localhost', help='host address')
    server_group.add_argument('-p', dest='port', type=int, default=8080, help='port number')

    parser.add_argument('-g', dest='group_name', type=str, default='samples', help='group name')

    kv_group = parser.add_argument_group('key-value for get test')
    kv_group.add_argument('-k', type=str, default='type', help='sample key in log dict')
    kv_group.add_argument('-v', type=str, default='sample', help='sample value in log dict')

    n_group = parser.add_argument_group('log data length and number')
    n_group.add_argument('-d', dest='data_len', type=int, default=100, help='auto-generated data length in log dict')
    n_group.add_argument('-n', dest='num', type=int, default=1, help='number of generated logs')

    args = parser.parse_args()

    # POST sample logs
    status_code, result = post_logs(
        group_name=args.group_name,
        logs=generate_logs(args.num, date_len=args.data_len, key=args.k, value=args.v),
        host=args.host, port=args.port,
    )
    if status_code != 200:
        print(f'failed to post logs({status_code}): {result}')
        exit(1)
    print('post logs result ---')
    pprint(result)
    print()

    # GET sample logs
    status_code, result = get_key_value_matched_logs(
        group_name=args.group_name, key=args.k, value=args.v, host=args.host, port=args.port,
    )
    if status_code != 200:
        print(f'failed to get logs({status_code}): {result}')
        exit(1)
    print(f'get logs result ---')
    pprint(result)
    print(f'- total count={len(result["logs"])}')
