import json
from argparse import ArgumentParser
from typing import AnyStr

import urllib3
from httpx import AsyncClient

from bp_endpoint_search.helpers.logging import logger
from bp_endpoint_search.inventory import InventoryItem

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def build_sessions(item: InventoryItem, username: str, password: str) -> None:
    """connect to and authenticate against an APIC returns a async session.


    Args:
        item (InventoryItem): Generated inventory item for host loaded from inventory.yml file.
        username (str): username for authentication
        password (str): password for authentication

    Raises:
        ValueError: Error raised if unable to authenticate against APIC
    """

    logger.info(f"Authenticating against host: {item.name}")
    payload = {"aaaUser": {"attributes": {"name": username, "pwd": password}}}

    try:
        client = AsyncClient(base_url=f"{item.host}/api", verify=False)
        resp = await client.post("/aaaLogin.json", json=payload)
        logger.debug(f"Requested URL: {resp.request.url}")
        logger.debug(f"Response Code: {resp.status_code}")
        logger.debug(resp.json())
        if resp.is_success:
            token = resp.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
            cookie = dict(name="APIC-Cookie", value=token)
            client.cookies.set(**cookie)
        else:
            logger.error(resp.json())
            raise ValueError()
    except Exception as e:
        logger.error(
            f"Unable to build session to host: {item.name}, any queries will not be run against this host."
        )
        logger.debug(e)
        return

    logger.debug("adding client object to the inventory")

    item.client = client


async def query_client_endpoints(item: InventoryItem, query_params: AnyStr) -> dict:
    """run a query against the fvCEp class on the APIC

    Args:
        item (InventoryItem): Generated inventory item for host loaded from inventory.yml file.
        query_params (AnyStr): the query parameters to run against the APIC

    Returns:
        dict: the JSON response object from the APIC
    """
    # Skip items with no authenticated client
    if item.client is None:
        logger.debug(
            f"{item.name} has no authenticated client and as such no query will be run."
        )
        return dict(host=item.name, resp=None)
    logger.info(f"Running endpoint query against host: {item.name}")
    try:
        # Example Query: 'query-target-filter=and(wcard(fvCEp.dn,"uni/tn\-FRASER\-LAB/"),ne(fvCEp.bdDn, ""),eq(fvCEp.baseEpgDn, ""))'
        resp = await item.client.get(
            f"/node/class/fvCEp.json?{query_params}&rsp-subtree=full&rsp-subtree-class=fvIp,fvRsToVm,fvRsVm,fvRsHyper,tagTagDef,fvRsCEpToPathEp,fvPrimaryEncap,fvRsToEpMacTag&rsp-subtree-include=required"
        )
        logger.debug(f"Requested URL: {resp.request.url}")
        logger.debug(f"Response Code: {resp.status_code}")
        logger.debug(json.dumps(resp.json(), indent=2))
        if resp.is_success:
            return dict(host=item.name, resp=resp.json())
        else:
            logger.error(resp.json())
            raise ValueError()
    except Exception as e:
        logger.error(f"Unable to query to host: {item.name}")
        logger.debug(e)
        return dict(host=item.name, resp=None)


def build_query(args: ArgumentParser) -> str:
    """Generate an APIC query to be used

    Args:
        args (ArgumentParser): the arguements passed when running the script

    Returns:
        str: query string to run against APIC
    """

    # Handle MAC search
    if args.subparser_name == "mac":
        logger.info("Building MAC search query")
        q_match = "eq"
        if args.partial_match:
            q_match = "wcard"
        return f'query-target-filter=and({q_match}(fvCEp.mac,"{args.mac_address}"))'

    # Handle IP search
    if args.subparser_name == "ip":
        logger.info("Building IP search query")

        if args.ip_address:
            if args.partial_match:
                return f'rsp-subtree-filter=and(wcard(fvIp.dn,"{args.ip_address}"))'
            else:
                return f'rsp-subtree-filter=eq(fvIp.addr,"{args.ip_address}")'
        elif args.ip_network:
            return f'rsp-subtree-filter=and(wcard(fvIp.addr,"{args.ip_network}"))'

    # Handle Node search
    if args.subparser_name == "node":
        logger.info("Building Node search query")
        return f'rsp-subtree-filter=and(wcard(fvRsCEpToPathEp.tDn,"{args.node}"))'