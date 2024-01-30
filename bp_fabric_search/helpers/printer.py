from prettytable import PrettyTable

from bp_fabric_search.helpers.logging import logger


def build_endpoint_table_row(host: str, resp_entry: dict) -> tuple:
    """build out table frow for endpoint search data

    Args:
        host (str): the hostname from the query
        resp_entry (dict): an fvCEp line entry from the resp data

    Returns:
        tuple: return a tuple of the table row to be added
    """

    # Set Default Data
    mac = ""
    ip = []
    tenant = ""
    epg = ""
    encap = []
    node = []
    interface = []
    source = ""

    try:
        mac = resp_entry["fvCEp"]["attributes"]["mac"]
    except KeyError:
        pass

    try:
        source = resp_entry["fvCEp"]["attributes"]["lcC"]
    except KeyError:
        pass

    # Update EPG
    if "epg-" in resp_entry["fvCEp"]["attributes"]["dn"]:
        epg = resp_entry["fvCEp"]["attributes"]["dn"].split("/")[3][4:]

    if "tn-" in resp_entry["fvCEp"]["attributes"]["dn"]:
        tenant = resp_entry["fvCEp"]["attributes"]["dn"].split("/")[1][3:]

    # Look for IP entry
    for child in resp_entry["fvCEp"]["children"]:
        if "fvIp" in child:
            ip.append(child["fvIp"]["attributes"]["addr"])
            node.append(child["fvIp"]["attributes"]["fabricPathDn"].split("/")[2][6:])
            interface.append(
                child["fvIp"]["attributes"]["fabricPathDn"].split("[")[-1].strip("]")
            )

            # Handle VMM that is unknown at IP level
            try:
                if child["fvIp"]["attributes"]["encap"] != "unknown":
                    encap.append(child["fvIp"]["attributes"]["encap"][5:])
            except KeyError:
                logger.debug("Unable to find encap key at fvIP level")
                pass

    # Overide default encap if none set
    if len(encap) == 0:
        encap.append(resp_entry["fvCEp"]["attributes"]["encap"][5:])

    # override deafult node and interface is none set
    if len(interface) == 0:
        interface.append(
            resp_entry["fvCEp"]["attributes"]["fabricPathDn"].split("[")[-1].strip("]")
        )
    if len(node) == 0:
        try:
            node.append(
                resp_entry["fvCEp"]["attributes"]["fabricPathDn"].split("/")[2][6:]
            )
        except IndexError as e:
            # unable to add node
            logger.debug("Unable to add node")
            logger.debug(e)
    return (
        host,
        mac,
        "\n".join(ip),
        tenant,
        epg,
        "\n".join(encap),
        "\n".join(node),
        "\n".join(interface),
        source,
    )


def build_route_table_row(host: str, resp_entry: dict) -> tuple:
    """build out table frow for route search data

    Args:
        host (str): the hostname from the query
        resp_entry (dict): an uribv4Route line entry from the resp data

    Returns:
        tuple: return a tuple of the table row to be added
    """

    # Set Default Data
    route = resp_entry["uribv4Route"]["attributes"]["prefix"]
    metric = []
    pref = []
    node = resp_entry["uribv4Route"]["attributes"]["dn"].split("/")[2].split("-")[-1]
    next_hop = []
    interface = []
    route_type = []
    vrf = []

    for next_hops in resp_entry["uribv4Route"]["children"]:
        next_hop.append(next_hops["uribv4Nexthop"]["attributes"]["addr"])
        interface.append(next_hops["uribv4Nexthop"]["attributes"]["if"])
        metric.append(next_hops["uribv4Nexthop"]["attributes"]["metric"])
        pref.append(next_hops["uribv4Nexthop"]["attributes"]["pref"])
        route_type.append(next_hops["uribv4Nexthop"]["attributes"]["routeType"])
        vrf.append(next_hops["uribv4Nexthop"]["attributes"]["vrf"])

    return (
        host,
        route,
        "\n".join(route_type),
        "\n".join(metric),
        "\n".join(pref),
        "\n".join(next_hop),
        node,
        "\n".join(interface),
        "\n".join(vrf),
    )


def print_endpoint_table(data: list, query: str, time_taken: str) -> None:
    """Prettyprint the responses to the users screen

    Example Item from the data:

    {
      "fvCEp": {
        "attributes": {
          "annotation": "",
          "baseEpgDn": "",
          "bdDn": "",
          "childAction": "",
          "contName": "",
          "dn": "uni/tn-common/ctx-SITE-2-TRANSIT/cep-4C:E1:76:97:1A:A7",
          "encap": "vlan-3101",
          "esgUsegDn": "",
          "extMngdBy": "",
          "fabricPathDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
          "hostingServer": "",
          "id": "0",
          "idepdn": "",
          "lcC": "learned",
          "lcOwn": "local",
          "mac": "4C:E1:76:97:1A:A7",
          "mcastAddr": "not-applicable",
          "modTs": "2023-10-20T10:05:30.016+00:00",
          "monPolDn": "uni/tn-common/monepg-default",
          "name": "4C:E1:76:97:1A:A7",
          "nameAlias": "",
          "reportingControllerName": "",
          "status": "",
          "uid": "0",
          "userdom": "all",
          "uuid": "",
          "vmmSrc": "",
          "vrfDn": "uni/tn-common/ctx-SITE-2-TRANSIT"
        },
        "children": [
          {
            "fvIp": {
              "attributes": {
                "addr": "10.98.252.251",
                "annotation": "",
                "baseEpgDn": "",
                "bdDn": "",
                "childAction": "",
                "createTs": "2023-12-16T11:17:55.342+00:00",
                "debugMACMessage": "",
                "encap": "vlan-3101",
                "esgUsegDn": "",
                "extMngdBy": "",
                "fabricPathDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                "flags": "",
                "lcOwn": "local",
                "modTs": "2023-12-16T11:17:56.137+00:00",
                "monPolDn": "uni/tn-common/monepg-default",
                "rn": "ip-[10.98.252.251]",
                "status": "",
                "uid": "0",
                "userdom": "all",
                "vrfDn": "uni/tn-common/ctx-SITE-2-TRANSIT"
              },
              "children": [
                {
                  "fvReportingNode": {
                    "attributes": {
                      "childAction": "",
                      "createTs": "2023-12-16T11:17:28.745+00:00",
                      "id": "101",
                      "lcC": "",
                      "lcOwn": "local",
                      "modTs": "2023-12-16T11:17:56.137+00:00",
                      "rn": "node-101",
                      "status": ""
                    }
                  }
                }
              ]
            }
          },
          {
            "fvIp": {
              "attributes": {
                "addr": "10.98.252.253",
                "annotation": "",
                "baseEpgDn": "",
                "bdDn": "",
                "childAction": "",
                "createTs": "2023-10-18T12:55:32.608+00:00",
                "debugMACMessage": "",
                "encap": "vlan-3100",
                "esgUsegDn": "",
                "extMngdBy": "",
                "fabricPathDn": "topology/pod-2/paths-2101/pathep-[eth1/1]",
                "flags": "",
                "lcOwn": "local",
                "modTs": "2023-10-18T12:55:33.403+00:00",
                "monPolDn": "uni/tn-common/monepg-default",
                "rn": "ip-[10.98.252.253]",
                "status": "",
                "uid": "0",
                "userdom": "all",
                "vrfDn": "uni/tn-common/ctx-SITE-2-TRANSIT"
              },
              "children": [
                {
                  "fvReportingNode": {
                    "attributes": {
                      "childAction": "",
                      "createTs": "2023-10-18T12:54:58.407+00:00",
                      "id": "2101",
                      "lcC": "",
                      "lcOwn": "local",
                      "modTs": "2023-10-18T12:55:33.403+00:00",
                      "rn": "node-2101",
                      "status": ""
                    }
                  }
                }
              ]
            }
          },
          {
            "fvRsCEpToPathEp": {
              "attributes": {
                "childAction": "",
                "forceResolve": "yes",
                "lcC": "learned",
                "lcOwn": "local",
                "modTs": "2023-12-16T11:17:56.137+00:00",
                "rType": "mo",
                "rn": "rscEpToPathEp-[topology/pod-1/paths-101/pathep-[eth1/1]]",
                "state": "formed",
                "stateQual": "none",
                "status": "",
                "tCl": "fabricAPathEp",
                "tDn": "topology/pod-1/paths-101/pathep-[eth1/1]",
                "tType": "mo"
              }
            }
          },
          {
            "fvRsCEpToPathEp": {
              "attributes": {
                "childAction": "",
                "forceResolve": "yes",
                "lcC": "learned",
                "lcOwn": "local",
                "modTs": "2023-10-18T12:55:33.403+00:00",
                "rType": "mo",
                "rn": "rscEpToPathEp-[topology/pod-2/paths-2101/pathep-[eth1/1]]",
                "state": "formed",
                "stateQual": "none",
                "status": "",
                "tCl": "fabricAPathEp",
                "tDn": "topology/pod-2/paths-2101/pathep-[eth1/1]",
                "tType": "mo"
              }
            }
          }
        ]
      }
    }


    Args:
        data (list): list of apic responses
    """

    table = PrettyTable()

    table.field_names = [
        "Host",
        "MAC",
        "IP",
        "Tenant",
        "EPG",
        "Encap",
        "Node",
        "Interface",
        "Source",
    ]
    skipped_hosts = []

    for host_resp in data:
        if host_resp["resp"] is None:
            skipped_hosts.append(host_resp["host"])
            continue

        table.add_rows(
            [
                build_endpoint_table_row(host=host_resp["host"], resp_entry=entry)
                for entry in host_resp["resp"]["imdata"]
            ]
        )

    print("\n")
    if skipped_hosts:
        print(f"Skipped Hosts: {', '.join(skipped_hosts)}")
    print(f"Query Type: {query.subparser_name}")
    print(f"Time taken: {time_taken} seconds.")
    print("\n")
    print(table)


def print_route_table(data: list, query: str, time_taken: str) -> None:
    """Prettyprint the responses to the users screen

    Example Item from the data:



    Args:
        data (list): list of apic responses
    """

    table = PrettyTable()

    table.field_names = [
        "Host",
        "Route",
        "Type",
        "Metric",
        "Pref",
        "Next Hop",
        "Node",
        "Interface",
        "Vrf",
    ]
    skipped_hosts = []

    for host_resp in data:
        if host_resp["resp"] is None:
            skipped_hosts.append(host_resp["host"])
            continue

        table.add_rows(
            [
                build_route_table_row(host=host_resp["host"], resp_entry=entry)
                for entry in host_resp["resp"]["imdata"]
            ]
        )

    print("\n")
    if skipped_hosts:
        print(f"Skipped Hosts: {', '.join(skipped_hosts)}")
    print(f"Query Type: {query.subparser_name}")
    print(f"Time taken: {time_taken} seconds.")
    print("\n")
    print(table)
