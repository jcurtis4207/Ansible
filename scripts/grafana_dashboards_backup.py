#!/usr/bin/env python3

import json
import os
import glob
import requests
import tarfile
import datetime
import argparse

BACKUP_DIR = '/root/backups'


def main():
    api_key = gather_args()

    headers = {'Authorization': f'Bearer {api_key}'}
    url = 'http://127.0.0.1:3000'

    delete_old_backups()
    board_links = fetch_board_links(url, headers)
    backup_dashboards(url, headers, board_links)
    create_archive()


def gather_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--api-key', type=str, required=True, help="API Key for Grafana user")
    args = parser.parse_args()
    return args.api_key


def delete_old_backups():
    print("Deleting previous backups")
    for f in glob.glob(f'{BACKUP_DIR}/*'):
        os.remove(f)


def fetch_board_links(url, headers):
    response = requests.get(f'{url}/api/search?query=&', headers=headers)

    if response.status_code != 200:
        raise Exception('Failed to fetch dashboard links\n{}'.format(response.text))

    return response.json()


def backup_dashboards(url, headers, board_links):
    for board in board_links:
        print(f'Saving: {board["title"]}')
        response = requests.get(f'{url}/api/dashboards/uid/{board["uid"]}', headers=headers)

        if response.status_code != 200:
            print("Failed to backup dashboard: {}".format(response.text))
            continue

        data_json = json.dumps(response.json()['dashboard'],
                               sort_keys=True,
                               indent=2,
                               separators=(',', ': '))

        with open(f'{BACKUP_DIR}/{board["uid"]}.json', 'w') as f:
            f.write(data_json)


def create_archive():
    print("Creating tar archive")
    timestamp = '{:%Y%m%dT%H%M%S}'.format(datetime.datetime.now())
    tar = tarfile.open(f'/{BACKUP_DIR}/dashboards_{timestamp}.tgz', 'w:gz')

    for f in glob.glob(f'{BACKUP_DIR}/*.json'):
        tar.add(f, arcname=os.path.basename(f))

    tar.close()


if __name__ == '__main__':
    main()
