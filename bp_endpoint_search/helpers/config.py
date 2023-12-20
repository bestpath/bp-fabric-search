import os

from dotenv import dotenv_values

SETTINGS = {
    "INVENTORY_USERNAME": os.environ.get("INVENTORY_USERNAME"),
    "INVENTORY_PASSWORD": os.environ.get("INVENTORY_PASSWORD"),
    "INVENTORY_PATH": os.environ.get("INVENTORY_PATH", "inventory.yml"),
    **dotenv_values(".env"),
}
