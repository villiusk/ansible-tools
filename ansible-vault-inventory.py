#!/usr/bin/python3


import os
import json
import requests
import argparse

KV_PATH = "kv/ansible/klientas1/"

VAULT_ADDR = os.getenv('VAULT_ADDR')
VAULT_TOKEN = os.getenv('VAULT_TOKEN')

hosts_group=KV_PATH.split("/")[-2]


def get_hosts_list():
    url = f"{VAULT_ADDR}/v1/{KV_PATH}?list=true"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {}

    response_data = json.loads(response.text)
    host_data = response_data["data"]

    return host_data['keys']


def get_host_data(hostname):
    url = f"{VAULT_ADDR}/v1/{KV_PATH}{hostname}"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {}

    response_data = json.loads(response.text)
    host_data = response_data["data"]

    return host_data

def generate_inventory(hosts_group):
    inventory = {"_meta": {"hostvars": {}}}
    hosts_list= get_hosts_list()

    for hostname in hosts_list:
        #if not hostname:
        #    continue

        host_data = get_host_data(hostname)
        #if not host_data:
        #    continue

        #inventory[hostname] = {"hosts": [hostname], "vars": host_data}
        inventory[hosts_group] = {"hosts": hosts_list}

        inventory["_meta"]["hostvars"][hostname] = host_data

    return inventory


def main():
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory script")
    parser.add_argument("--list", help="List all hosts (default)", action="store_true")
    parser.add_argument("--host", help="Get host information")
    args = parser.parse_args()

    if args.host:
        host_data = get_host_data(args.host)
        if host_data:
            print(json.dumps(host_data))
        else:
            print(json.dumps({}))
    else:
        inventory = generate_inventory(hosts_group)
        print(json.dumps(inventory))

if __name__ == "__main__":
    main()

