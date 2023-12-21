import argparse
import asyncio
import sys
import time
from argparse import ArgumentParser

from bp_fabric_search.helpers.apic import (build_query, build_sessions,
                                           query_clients)
from bp_fabric_search.helpers.config import SETTINGS
from bp_fabric_search.helpers.logging import configure_logger, logger
from bp_fabric_search.helpers.printer import (print_endpoint_table,
                                              print_route_table)
from bp_fabric_search.inventory import Inventory


def parse_args(args) -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Endpoint query script",
        usage="endpoint-search [options]",
        description="Script iterate over an inventory file and search for endpoints.",
    )
    # create parent subparser for 'loglevel' key.
    parent_log_parser = argparse.ArgumentParser(add_help=False)
    parent_log_parser.add_argument(
        "-log",
        "--loglevel",
        default="info",
        dest="loglevel",
        choices=["info", "debug", "warning", "error", "critical"],
        help="""Provide logging level, default=info.
        Example: --loglevel info""",
    )
    subparsers = parser.add_subparsers(
        dest="subparser_name", required=True, help="sub-command help"
    )

    # create the parser for the "mac" command
    parser_mac = subparsers.add_parser(
        "mac",
        parents=[parent_log_parser],
        help="Search endpoints based on MAC address",
    )
    parser_mac.add_argument(
        "--mac-address",
        "-m",
        dest="mac_address",
        type=str,
        required=True,
        help="Mac Address for example: 00:50:56:85:EF:89",
    )

    parser_mac.add_argument(
        "--partial",
        "-p",
        dest="partial_match",
        action="store_true",
        required=False,
        help="Whether to require a full mac entry or a wildcard match",
    )

    # create the parser for the "ip" command
    parser_ip = subparsers.add_parser(
        "ip",
        parents=[parent_log_parser],
        help="Search endpoints based on IP address or network",
    )
    parser_ip.add_argument(
        "--host",
        dest="ip_address",
        type=str,
        required=False,
        help="IP Address for example: 10.96.255.10",
    )

    parser_ip.add_argument(
        "--network",
        dest="ip_network",
        type=str,
        required=False,
        help="Network Address for example: 10.0.0.0/8",
    )

    parser_ip.add_argument(
        "--partial",
        "-p",
        dest="partial_match",
        action="store_true",
        required=False,
        help="Whether to require a full ip entry or a wildcard match",
    )

    # create the parser for the "node" command
    parser_node = subparsers.add_parser(
        "node",
        parents=[parent_log_parser],
        help="Search endpoints based on Node",
    )
    parser_node.add_argument(
        "--id",
        dest="node",
        type=str,
        required=False,
        help="Node ID to query",
    )

    # create the parser for the "route" command
    parser_route = subparsers.add_parser(
        "route",
        parents=[parent_log_parser],
        help="Search routes based on network",
    )
    parser_route.add_argument(
        "--prefix",
        dest="prefix",
        type=str,
        required=True,
        help="Prefix ID to query",
    )

    parser_route.add_argument(
        "--vrf",
        dest="vrf",
        type=str,
        required=False,
        help="Filter route search by VRF",
    )

    parser_route.add_argument(
        "--exact",
        dest="exact",
        action="store_true",
        required=False,
        help="Whether the prefix should be an exact match",
    )

    return parser.parse_args(args)


async def start(args: ArgumentParser):
    # record the starting time
    start = time.perf_counter()
    inventory = Inventory()

    session_tasks = [
        build_sessions(
            item=item,
            username=SETTINGS["INVENTORY_USERNAME"],
            password=SETTINGS["INVENTORY_PASSWORD"],
        )
        for item in inventory.items
    ]

    await asyncio.gather(*session_tasks)

    query = build_query(args=args)

    query_tasks = [
        query_clients(
            item=item,
            query=query,
        )
        for item in inventory.items
    ]

    query_resp = await asyncio.gather(*query_tasks)
    logger.debug("APIC Responses:")
    logger.debug(query_resp)

    # record the ending time
    end = time.perf_counter()
    time_taken = f"{end - start:.2f}"
    logger.debug(f"Time taken: {time_taken} seconds.")

    # Print the table of responses
    if args.subparser_name in ["mac", "ip", "node"]:
        print_endpoint_table(data=query_resp, query=args, time_taken=time_taken)
    elif args.subparser_name in ["route"]:
        print_route_table(data=query_resp, query=args, time_taken=time_taken)


def main():
    args = parse_args(sys.argv[1:])
    configure_logger(args.loglevel)

    if SETTINGS["INVENTORY_USERNAME"] is None or SETTINGS["INVENTORY_PASSWORD"] is None:
        logger.error(
            '"INVENTORY_USERNAME" or "INVENTORY_PASSWORD" is undefined, please ensure the are set as environment variables or within a .env file.'
        )
        sys.exit(1)

    asyncio.run(start(args=args))


if __name__ == "__main__":
    main()
