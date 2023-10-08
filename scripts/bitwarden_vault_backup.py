#!/usr/bin/env python3

import subprocess
import json
import os
import glob
import argparse

BW_CLI = '/usr/local/bin/bw'
TEMP_DIR = '/root/temp'
BACKUP_DIR = '/root/backups'


def setup():
    if not os.path.isdir(TEMP_DIR):
        raise Exception("Temp directory does not exist")
    if not os.path.isdir(BACKUP_DIR):
        raise Exception("Backup directory does not exist")
    for f in glob.glob(f'{BACKUP_DIR}/*'):
        os.remove(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', type=str, required=True, help="Bitwarden Username")
    parser.add_argument('-p', '--password', type=str, required=True, help="Bitwarden Password")
    args = parser.parse_args()

    global USER
    global PWD
    USER = args.user
    PWD = args.password


def login():
    print("Perfoming login...")
    status = get_login_status()
    if status != 'unauthenticated':
        return

    subprocess.run([BW_CLI, 'login', USER, PWD, '--method', '0', '--quiet'])
    status = get_login_status()
    if status == 'unauthenticated':
        raise Exception('ERROR: Failed to authenticate')


def get_login_status():
    status = subprocess.run([BW_CLI, 'status'], capture_output=True, check=False)
    return json.loads(status.stdout)['status']


def unlock():
    unlock_output = subprocess.run([BW_CLI, 'unlock', PWD, '--raw'], capture_output=True, check=True)
    session_key = unlock_output.stdout.decode('utf-8')
    if session_key == '':
        raise Exception('ERROR: Failed to unlock vault')
    print("Login successful")
    return session_key


def export(session_key):
    print("Perfoming vault export...")
    env_vars = f'BW_SESSION={session_key}'
    output = subprocess.run(['env', env_vars, BW_CLI, 'export', '--format', 'json', '--output', f'{TEMP_DIR}/'],
                            capture_output=True, check=True)
    print("Vault export complete")
    filename = output.stdout.decode('utf-8').split(' ')[-1]
    return filename


def encrypt_vault(input_file):
    print("Encrypting vault...")
    output_file = f'{BACKUP_DIR}/{os.path.basename(input_file)}.gpg'
    subprocess.run(['gpg', '--batch', '--yes', '--passphrase-file=/etc/gpg_creds', '-o', output_file, '-c', input_file],
                   check=True)
    print("Encryption successful")


def cleanup():
    for f in glob.glob(f'{TEMP_DIR}/*'):
        os.remove(f)
    subprocess.run([BW_CLI, 'logout'], check=False)


def main():
    try:
        setup()
        login()
        key = unlock()
        vault_file = export(key)
        encrypt_vault(vault_file)
    finally:
        cleanup()


if __name__ == '__main__':
    main()
