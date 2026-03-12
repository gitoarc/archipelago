from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World
from . import items, locations, options, regions, rules, web_world
from .enums import BOH_StrEnums


class BOHWorld(World):
    """
    Restore a crumbling occult library by a winter sea.
    Build the world’s foremost collection of grimoires and arcana. Master the invisible arts.
    BOOK OF HOURS is a narrative crafting RPG set in a 1930s world of hidden gods and secret histories.
    What sort of Librarian will you choose to be?
    (Weather Factory, 2023)
    """
    game = "Book of Hours"

    # The WebWorld is a definition class that governs how this world will be displayed on the website.
    web = web_world.BohWeb()

    # This is how we associate the options defined in our options.py with our world.
    options_dataclass = options.BoHOptions
    options: options.BoHOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).


    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = BOH_StrEnums.OriginRegionName

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    # world class must also have a create_item function
    def create_item(self, name: str) -> items.BOHItem:
        return items.create_item_with_auto_classification(self, name)

    # your world *must* have at least one infinitely repeatable item (usually filler).
    # You must override this function and return this infinitely repeatable item's name.
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    # There may be data that the game client will need to modify the behavior of the game.
    # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
    # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data: dict[str, Any] = {
            "memory_progression": self.options.memory_progression.value,
            "victory_shards": len([a for a in self.get_locations() if a.item.name == "Victory Shard"])
        }
        return slot_data
