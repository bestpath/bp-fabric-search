# Endpoint Search

Quickly search for endpoints across a large number of APIC's and display the results in a table.

Endpoints can be searched using the following criteria:
- MAC Address
- IP Address
- IP Network
- Node

It is also possible to do searches based on partial data. for example the last 4 characters of a MAC address.

# Installation

```bash
pip install bp-endpoint-search
```

# Usage

## Inventory File

An simple inventory file is used to store a list of APIC's to search. This is a YAML file with a name and host key

```yaml
---
- name: UKLDN-DC1
  host: https://10.96.255.1
- name: UKLDN-DC2
  host: https://10.98.255.1
```

## Environment Variables

The following environment variables are required for the script to run, these can be set using 
the `EXPORT` command or loaded in at runtime from a .env file.

```env
INVENTORY_USERNAME="USERNAME"
INVENTORY_PASSWORD="PASSWORD"

# Optional value for path to inventory file
# if not included it will default to inventory.yml

INVENTORY_PATH=path/to/my/inventory.yml
```

## Search by Node
```bash
endpoint-search node --id 101
```
## Search by MAC
```bash
endpoint-search mac -m 00:50:56:85:6F:F9
```

## Search by Network / IP
```bash
endpoint-search ip --network 10.96.0.0/16
```

```bash
endpoint-search ip --host 10.96.252.1
```

## Result
```bash
Skipped Hosts: 
Time taken: 0.20 seconds.


+--------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
|  Host  |        MAC        |       IP      |     Tenant    | EPG | Encap | Node | Interface |  Source |
+--------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
| APIC-1 | 00:50:56:85:EF:89 | 10.96.252.102 | LSEG-TENANT-2 |     |  1411 | 101  |  eth1/10  | learned |
| APIC-1 | 00:50:56:85:EF:89 |  10.96.252.86 | LSEG-NET-SVCS |     |  1413 | 101  |  eth1/10  | learned |
+--------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
```