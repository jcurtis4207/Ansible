Deployment
=========

An Ansible role for deploying Linux machines.

The role currently supports the following platforms:
* Raspberry Pi
* Ubuntu and Debian Virtual Machines
* Rocky and Debian LXC Containers

Role Variables
--------------

1. Default package lists for each package manager:

```yaml
deployment_apt_package_list:
  - git
  - vim
  - vifm
  - python3
  - python3-pip
  - rsync

deployment_dnf_package_list:
  - git
  - vim
  - python3
  - python3-pip
  - rsync
  - wget
```

2. Directory for cloning dotfiles:

```yaml
deployment_dotfiles_directory: /tmp/Dotfiles
```

3. SSH Public Key for main desktop machine:

```yaml
deployment_beowulf_ssh_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILbBc7ct57HcSGWoIdqjDPhEmU5iC8hBoEMHao68eN6C jacob@Beowulf"
```

Optional Variables
------------------

1. Hostname and static IP to set during deployment

```yaml
deployment_hostname: ansible-debian
deployment_static_ip: 192.168.1.201
```

Example Playbook
----------------

```yaml
---
- name: Deploy New Machine
  hosts: new
  gather_facts: no
  tasks:
    - name: Deploy
      import_role:
        name: deployment
```

License
-------

BSD

Author Information
------------------

Written by Jacob Curtis, 2023.
