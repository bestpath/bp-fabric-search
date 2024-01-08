# Fabric Search

Quickly search endpoints and routing tables across a large number of APIC's and display the results in a table.

Endpoints can be searched using the following criteria:

- MAC Address
- IP Address
- IP Network
- Node

Route can be search using the following criteria:

- Prefix
- VRF

It is also possible to do searches based on partial data. for example the last 4 characters of a MAC address.

# Installation

```bash
pip install bp-fabric-search
```

# Usage

## Inventory File

An simple inventory file is used to store a list of APIC's to search. This is a YAML file with a name and host key

```yaml
---
- name: FABRIC-1
  host: https://10.1.0.1
- name: FABRIC-2
  host: https://10.2.0.1
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

## Endpoint Searches

### Search by Node

```bash
fabric-search node --id 101
```

### Search by MAC

```bash
fabric-search mac -m 00:50:56:85:6F:F9
```

### Search by Network / IP

```bash
fabric-search ip --network 10.96.0.0/16
```

```bash
fabric-search ip --host 10.96.252.1
```

## Result

```bash
Skipped Hosts:
Time taken: 0.20 seconds.


+----------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
|  Host    |        MAC        |       IP      |     Tenant    | EPG | Encap | Node | Interface |  Source |
+----------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
| FABRIC-1 | 00:50:56:85:EF:89 | 10.96.252.102 | CUST-TENANT-2 |     |  1411 | 101  |  eth1/10  | learned |
| FABRIC-1 | 00:50:56:85:EF:89 |  10.96.252.86 | CUST-NET-SVCS |     |  1413 | 101  |  eth1/10  | learned |
+----------+-------------------+---------------+---------------+-----+-------+------+-----------+---------+
```

## Route Searches

### Search by Prefix

```bash
fabric-search route --prefix 10.96.0.0/24
```

### Search by Prefix and VRF

```bash
fabric-search route --prefix 10.96.0.0/24 --vrf FRASER-LAB:FRASER-LAB
```

### Search by exact prefix

```bash
fabric-search route --prefix 10.96.0.0/24 --exact
```

## Result

```bash
Skipped Hosts: FABRIC-2
Query Type: route
Time taken: 5.13 seconds.


+-----------+---------------+-------+--------+------+------------------+------+-------------+-----------------------+
|    Host   |     Route     |  Type | Metric | Pref |     Next Hop     | Node |  Interface  |          Vrf          |
+-----------+---------------+-------+--------+------+------------------+------+-------------+-----------------------+
| FABRIC-1  |   0.0.0.0/0   |  ebgp |   0    |  20  | 10.96.252.255/32 | 102  | unspecified | FRASER-LAB:FRASER-LAB |
| FABRIC-1  | 10.96.0.30/32 | local |   0    |  0   |  10.96.0.30/32   | 102  |    vlan25   | FRASER-LAB:FRASER-LAB |
| FABRIC-1  | 10.96.0.62/32 | local |   0    |  0   |  10.96.0.62/32   | 102  |    vlan23   | FRASER-LAB:FRASER-LAB |
| FABRIC-1  |   0.0.0.0/0   |  ebgp |   0    |  20  | 10.96.252.253/32 | 101  | unspecified | FRASER-LAB:FRASER-LAB |
| FABRIC-1  | 10.96.0.30/32 | local |   0    |  0   |  10.96.0.30/32   | 101  |    vlan23   | FRASER-LAB:FRASER-LAB |
| FABRIC-1  | 10.96.0.62/32 | local |   0    |  0   |  10.96.0.62/32   | 101  |    vlan29   | FRASER-LAB:FRASER-LAB |
+-----------+---------------+-------+--------+------+------------------+------+-------------+-----------------------+
```
