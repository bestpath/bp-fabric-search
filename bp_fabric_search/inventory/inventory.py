import os
from typing import List, Optional

import yaml
from httpx import AsyncClient
from pydantic import BaseModel, HttpUrl, TypeAdapter

from bp_fabric_search.helpers.config import SETTINGS
from bp_fabric_search.helpers.logging import logger


class InventoryItem(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    host: HttpUrl
    client: Optional[AsyncClient] = None


class Inventory:
    def __init__(self):
        self.inventory_path = SETTINGS["INVENTORY_PATH"]
        self.items = List[InventoryItem]

        # load inventory
        self.load_inventory()

    def load_inventory(self) -> None:
        """Load inventory data from yml source"""
        logger.info("Loading inventory data.")
        try:
            with open(self.inventory_path, "r") as f:
                data = yaml.safe_load(f)
                inventory = TypeAdapter(List[InventoryItem])
                self.items = inventory.validate_python(data)

        except FileNotFoundError as e:
            logger.error(
                f"Unable to find inventory file at path: {self.inventory_path}"
            )
            logger.debug(e)
