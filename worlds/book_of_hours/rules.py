from __future__ import annotations

import re
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, CollectionState, Location
from .enums import BOH_StrEnums
from .functions import int_from_roman_in_wt_node, to_roman
from .items import BOHItem
from .jsondump import terrains, memories, memories_post_house

if TYPE_CHECKING:
    from .world import BOHWorld


def set_all_rules(world: BOHWorld) -> None:
    # Note: Regions do not have rules, the Entrances connecting them do!
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: BOHWorld) -> None:
    entrances = [n for n in world.get_entrances()]
    lodge_exits = [n for n in entrances if n.parent_region.name == BOH_StrEnums.KeepersLodge]
    for e in lodge_exits:
        world.set_rule(e, lambda state: state.has("Hush House Key", world.player))

def set_all_location_rules(world: BOHWorld) -> None:
    locations = [a for a in world.get_locations()]
    if world.options.memorinsanity.is_enabled:
        # basic memories (talk with villager / weather) can be acquired pre-house, but everything else requires read/craft/the HOUSE
        for m in memories_post_house:
            # !! f"Remember a {m.Label}" IN a.name  finds EarthquakeName/WeatherEquake; Find fix to avoid that
            for loc in [a for a in locations if re.match(f'Remember an? {m.Label}' , a.name)]:
                loc.access_rule = lambda state: state.can_reach(BOH_StrEnums.WatchmansTowerGatehouse, "Region", world.player)

    if world.options.memory_progression.is_enabled:
        pass
        # event rules assigned on creation, check locations.py

    if world.options.insanitree:
        wt = world.get_region(BOH_StrEnums.TreeOfWisdoms)
        locs:list[Location] =  [a for a in wt.locations]

        for z, i in enumerate(range(world.options.insanitree.from_, 1+world.options.insanitree.to)):
            if z == 0:
                continue # The first path-nodes have no separate rule; They are controlled by region rule

            locs_in_tier = [a for a in locs if int_from_roman_in_wt_node(a.name) == i]

            for l in locs_in_tier:
                prev_loc_name = BOH_StrEnums.TreeOfWisdoms_Root if i == 1 else l.name.replace(to_roman(i), to_roman(i-1))
                [prev_loc] = [a for a in locs if a.name == prev_loc_name]
                l.access_rule = lambda state, pl=prev_loc: pl in state.locations_checked
    pass

def set_completion_condition(world: BOHWorld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(("Sword", "Shield"), world.player)

    option_names = [a for a in vars(world.options)]
    enabled_game_options = [world.options.__getattribute__(n) for n in option_names]
    # only my custom BOHOptions
    enabled_game_options = [a for a in enabled_game_options if getattr(a, "is_enabled", False)]

    goals_sum = len([a for a in world.get_locations() if a.item and a.item.name == "Victory Shard"])

    world.set_completion_rule(lambda state: state.has("Victory Shard", world.player, goals_sum))
