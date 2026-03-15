from __future__ import annotations

import Utils
from BaseClasses import Region, EntranceType
from .enums import BOH_StrEnums
from .jsondump import terrains, wisdomtree
from typing import TYPE_CHECKING

from .options import RoomGoal

if TYPE_CHECKING:
    from .world import BOHWorld


def create_and_connect_regions(world: BOHWorld) -> None:
    create_all_regions(world)
    connect_regions(world)
    if False:
        Utils.visualize_regions(world.get_region(BOH_StrEnums.OriginRegionName), "boh.puml")


def create_all_regions(world: BOHWorld) -> None:
    region_names:set[str] = {BOH_StrEnums.OriginRegionName}

    # Independant of options bc of some dependencies (Assistants only post-village possible...) and its easier for my assignments if I know they always exist;
    # If no option causes a region I can just not spawn the locations
    guaranteed_regions = [a for a in terrains if a.Label in [BOH_StrEnums.StBrandansCove.value, BOH_StrEnums.BrancrugVillage.value,
                                                             BOH_StrEnums.CucurbitBridge.value, BOH_StrEnums.KeepersLodge.value,
                                                             BOH_StrEnums.WatchmansTowerGatehouse.value]]
    for r in guaranteed_regions:
        region_names.add(r.Label)

    # Memories can not really be categorised into Regions imo

    # Souls are part of WisdomTree IN VANILLA, idk yet how/if randomiser can/will affect this
    if False:
        region_names.add("The Tree of Wisdoms")
    # Terrains

    if world.options.insanitree:
        # because of 'region_names' being a Set, I don't have to check "if exists, do not add"
        region_names.add(BOH_StrEnums.TreeOfWisdoms)

    regions = [Region(name, world.player, world.multiworld) for name in region_names]
    world.multiworld.regions += regions


def connect_regions(world: BOHWorld) -> None:
    origin_region = world.get_region(BOH_StrEnums.OriginRegionName)
    all_regions = world.get_regions()
    start_name = BOH_StrEnums.StBrandansCove
    origin_region.connect(world.get_region(start_name),
                                     f"Menu -> {start_name}")

    wt = [a for a in world.get_regions() if a.name == "The Tree of Wisdoms"]
    if len(wt) == 1:
        origin_region.connect(wt[0], f"Menu -> The Tree of Wisdoms")
    # Terrain connections
    unhandled: list[str] = [start_name]
    done: list[str] = []
    while len(unhandled) > 0:
        currentName = unhandled[0]
        #add self -> others connectors
        region = world.get_region(currentName)
        nexts = [connection.Label for t in terrains for connection in t.ConnectsTo if t.Label == currentName]
        n: str
        for n in nexts:
            # do NOT add a -> b -> a connections; it clutters the logic, methinks
            exist_in_world = len([a for a in all_regions if n in a.name]) == 1
            if exist_in_world and n not in done:
                x = region.connect(world.get_region(n), f"{currentName} -> {n}", None)  #set in rules.py
                x.randomization_type = EntranceType.TWO_WAY
                if n not in unhandled:
                    unhandled.append(n)

        done.append(currentName)
        unhandled.remove(currentName)

    if world.options.insanitree:
        wt = world.get_region(BOH_StrEnums.TreeOfWisdoms)
        # Bc any fireplace can dry the book, village is technically not a hard requirement
        origin_region.connect(wt)
