#!/usr/bin/env python3
#########################################################################
# Title:         Saltbox: Cloudflared | Manage Ingress Rules           #
# Author(s):     salty                                                  #
# URL:           https://github.com/saltyorg/Saltbox                    #
# --                                                                    #
#########################################################################
#                   GNU General Public License v3.0                     #
#########################################################################

import json
import sys
import yaml
from pathlib import Path

def load_config(config_path):
    """Load existing config or create default structure"""
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {'ingress': []}

def save_config(config_path, config):
    """Save config to YAML file"""
    # Ensure catch-all rule is last
    ingress = config.get('ingress', [])
    catch_all = {'service': 'http_status:404'}

    # Remove existing catch-all rules
    ingress = [rule for rule in ingress if rule.get('service') != 'http_status:404']

    # Add catch-all at the end
    ingress.append(catch_all)
    config['ingress'] = ingress

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def add_route(config_path, hostname, service):
    """Add or update a route in the config"""
    config = load_config(config_path)
    ingress = config.get('ingress', [])

    # Remove existing rule for this hostname if it exists
    ingress = [rule for rule in ingress if rule.get('hostname') != hostname]

    # Add new rule
    ingress.insert(0, {
        'hostname': hostname,
        'service': service
    })

    config['ingress'] = ingress
    save_config(config_path, config)
    print(f"Added route: {hostname} -> {service}")

def remove_route(config_path, hostname):
    """Remove a route from the config"""
    config = load_config(config_path)
    ingress = config.get('ingress', [])

    # Remove rule for this hostname
    ingress = [rule for rule in ingress if rule.get('hostname') != hostname]

    config['ingress'] = ingress
    save_config(config_path, config)
    print(f"Removed route: {hostname}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: manage_ingress.py <config_path> <action> [hostname] [service]")
        print("Actions: add, remove")
        sys.exit(1)

    config_path = sys.argv[1]
    action = sys.argv[2]

    if action == 'add':
        if len(sys.argv) != 5:
            print("Usage: manage_ingress.py <config_path> add <hostname> <service>")
            sys.exit(1)
        hostname = sys.argv[3]
        service = sys.argv[4]
        add_route(config_path, hostname, service)
    elif action == 'remove':
        if len(sys.argv) != 4:
            print("Usage: manage_ingress.py <config_path> remove <hostname>")
            sys.exit(1)
        hostname = sys.argv[3]
        remove_route(config_path, hostname)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
