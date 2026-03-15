from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location, ItemClassification, CollectionState
from . import items, enums
from .enums import BOH_StrEnums
from ._generate_locations import *
from .functions import predicate_with
from .items import BOHItem
from .jsondump import terrains, JsonParsed, memories, SimplePredicate, lessons, everything

if TYPE_CHECKING:
    from .world import BOHWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = (MEMORIES_SPECIFIC | MEMORIES_PILE
                       | SOULS_SPECIFIC | SOULS_PILE
                       | TERRAINS_SPECIFIC | TERRAINS_PILE
                       | BOOKS_SPECIFIC | BOOKS_PILE
                       | CATALOG_PILE_ANY | CATALOG_PILE_DAWN | CATALOG_PILE_SOLAR | CATALOG_PILE_BARONIAL | CATALOG_PILE_CURIA | CATALOG_PILE_NOCTURNAL
                       | WISDOMS_SPECIFIC | WISDOMS_PILE
                       #| LESSONS_SPECIFIC | LESSONS_PILE
                       | SKILLS_SPECIFIC | SKILLS_PILE)
pass


class BOHLocation(Location):
    game = "Book of Hours"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: BOHWorld) -> None:
    create_locations(world)
    create_events(world)




def create_locations_memory_progression(world: BOHWorld) -> None:
    menu = world.get_region("Menu")
    locations_wanted: int = world.options.memory_progression["locations"]
    rewards_per_loc: int = world.options.memory_progression.get("rewards_per_location", 1)

    # Time only starts after your introduction to the village acquantance.
    # Meaning 'weathers' are theoretically locked behind 'Brancrug Village Acquaintance'
    #  but basic, musics, ESPECIALLY lessons, etc... require the library rooms (or at MINIMUM the village acquaintance)
    # just streamline everything post-village? post-lodge? or stick in menu?
    locs = {k: v
            for k, v in MEMORIES_PILE.items()
            for l in range(1, 1 + locations_wanted)
            if f" {l} " in k}
    menu.add_locations(locs, BOHLocation)
    # placing goal item transforms the location to event, check create_events()

def create_locations_memorinsanity(world: BOHWorld) -> None:
    #assume this runs AFTER create_locations_memorinsanity_goals() "might" have added locations
    origin_region = world.get_region(BOH_StrEnums.OriginRegionName)
    world_locs = {l.name:l.address for l in world.get_locations()}
    options = dict(world.options.memorinsanity.value)
    for k,v in options.items():
        jsons = [a for a in memories+lessons if a.contains_substr(k)]
        locs = {k:v for k,v in MEMORIES_SPECIFIC.items() for j in jsons if j.Label in k }
        for lk, lv in locs.items():
            if lk in world_locs:
                pass
            else:
                origin_region.locations.append(BOHLocation(world.player,lk,lv,origin_region))
    wanteds = [a.Label for a in everything for o in options if a.contains_substr(o)]

def create_locations_memorinsanity_goals(world: BOHWorld):
    op = world.options.memorinsanity_goals
    s:str
    # first, accumulate the enabled locs
    dumped_loc_names:set[str] = set()
    for s in op:
        filterstring = s.split(":")[0]
        add = s.split(":")[1] == "1"
        filtersplits = filterstring.split("__")
        names = filtersplits[0].split(",")
        pred = filtersplits[1] if len(filtersplits) > 1 else "any>0"
        pred = SimplePredicate(pred)
        jl = {a.Label for a in memories for nam in names
              if a.contains_substr(nam) and pred.evaluate_on_dict(a.Aspects)}
        if add:
            dumped_loc_names.update(jl)
        else:
            dumped_loc_names -= jl
    pass
    # ...then, translate the list[str] to BOHLocations
    aa = {k:v for k,v in MEMORIES_SPECIFIC.items()
          for name in dumped_loc_names
          if name in k}
    # ...and add to world
    origin_region = world.get_region(BOH_StrEnums.OriginRegionName)
    for k,v in aa.items():
        loc = BOHLocation(world.player, k, None, origin_region)
        loc.place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, None, world.player))
        origin_region.locations.append(loc)


def create_locations_wisdoms(world: BOHWorld) -> None:
    origin_region = world.get_region(BOH_StrEnums.OriginRegionName)
    wt = world.get_region(BOH_StrEnums.TreeOfWisdoms)

    #wt.add_locations({k: v for k, v in WISDOMS_PILE.items()}, BOHLocation)
    #wt.add_locations({k: v for k, v in WISDOMS_TIERS.items()}, BOHLocation)
    for i in range(world.options.insanitree.from_, 1 + world.options.insanitree.to):
        if i == 0:
            locs = {k: v for k, v in WISDOMS_SPECIFIC.items() if k == BOH_StrEnums.TreeOfWisdoms_Root}
        else:
            dic = WISDOMS_SPECIFIC if world.options.insanitree.split_paths else WISDOMS_TIERS
            locs = {k: v for k, v in dic.items() if int_from_roman_in_wt_node(k) == i}
        loc_type_str = world.options.insanitree.location_progress_types[i]
        loc_type = LocationProgressType(int(loc_type_str))
        for k, v in locs.items():
            wt.locations.append(BOHLocation(world.player, k, v, wt))
            wt.locations[-1].progress_type = loc_type


def create_locations(world: BOHWorld) -> None:
    menu = world.get_region("Menu")
    village = world.get_region(BOH_StrEnums.BrancrugVillage)

    #######################################
    if world.options.memory_progression.is_enabled:
        create_locations_memory_progression(world)
    # since memorinsanity could roll NOT creating a loc but it is a memorinsanity_goal;
    #       mIns did not create loc -> InsGoal has to create
    #       mIns did create loc     -> Ins must check and modify loc instead
    # Instead, create the goals first and let memorinsanity "fill" its normal locations:
    #       InsGoal can create any locs
    #       mIns check if already exists before adding
    # Nr2 seems simpler; do memorinsanity_goals first:
    if world.options.memorinsanity_goals.is_enabled:
        create_locations_memorinsanity_goals(world)
    if world.options.memorinsanity.is_enabled:
        create_locations_memorinsanity(world)

    if world.options.insanitree:
        create_locations_wisdoms(world)

    if False:
        for unlockname, apid in TERRAINS_SPECIFIC.items():
            normname = unlockname.replace("Unlocked the ", "")
            region = world.get_region(normname)
            if normname == "St Brandan’s Cove" and 1 == 0:
                region.add_event(normname, None, None, BOHLocation, BOHItem)
                #world.set_rule(world.get_location(normname), True_())
            else:
                # find what room can connect to this
                roads: list[str] = [c.Label for e in terrains for c in e.ConnectsTo if c == normname]
                region.add_event(normname, None, None, BOHLocation, BOHItem, False)
                #world.set_rule(world.get_location(normname), HasAny(*roads))

            region.add_locations({unlockname: apid}, BOHLocation)
            #world.set_rule(world.get_location(unlockname), Has(unlockname))


def create_events(world: BOHWorld) -> None:
    menu = world.get_region("Menu")
    village = world.get_region(BOH_StrEnums.BrancrugVillage)
    lodge = world.get_region(BOH_StrEnums.KeepersLodge)

    # unlocking the village is not enough to unlock assistance and journal
    acquaint = BOHLocation(world.player, BOH_StrEnums.VillageAcquaintance, None, village)
    acquaint.place_locked_item(BOHItem(BOH_StrEnums.VillageAcquaintance, ItemClassification.progression, None, world.player))
    village.add_event(BOH_StrEnums.VillageAcquaintance, BOH_StrEnums.VillageAcquaintance,
                      None,
                      BOHLocation, BOHItem, False)
    #theoretically any "library.fireplace.*" workstation works, but Village is the earliest, and RoomRando is not really possible until post-village (NO way to get assistance)
    village.add_event(BOH_StrEnums.DriedJournal, BOH_StrEnums.DriedJournal,
                      lambda state: state.has(BOH_StrEnums.VillageAcquaintance, world.player),
                      BOHLocation, BOHItem, False)
    # static goal (just testing Hush Key rules)
    r = world.get_region(BOH_StrEnums.WatchmansTowerGatehouse)
    r.locations.append(BOHLocation(world.player, "Entered the House proper", None, lodge))
    r.locations[0].place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, None, world.player))
    world.set_rule(r.locations[0], lambda state: state.has("Hush House Key", world.player))

    if world.options.memory_progression.is_enabled:
        # place goal item at X
        loc = world.get_location(f"Remember {world.options.memory_progression.goal} memories")
        loc.address = None
        loc.place_locked_item(BOHItem("Victory Shard", ItemClassification.progression, None, world.player))

    if False:  #wisdom tree
        wt = world.get_region("The Tree of Wisdoms")

        l = [a for a in jsondump.wisdomtree if "locus" not in a.IdStr]
        _root = [a for a in jsondump.wisdomtree if a.IdStr == "wt.memorylocus"][0]

        wt.add_event("__event_wt.memorylocus", "__event_wt.memorylocus",
                     lambda state: state.can_reach_region("The Tree of Wisdoms", world.player), BOHLocation, BOHItem)
        for i in range(0, 9):  # == 9 paths
            _current_idstr = l[0].IdStr[:-1]
            _all_of_path = [a for a in l if _current_idstr in a.IdStr]
            assert len(_all_of_path) == 9
            e = [a for a in _all_of_path if ".1" in a.IdStr][0]
            l.remove(e)
            wt.add_event("__event_" + e.IdStr, "__event_" + e.IdStr,
                         lambda state: state.has("__event_wt.memorylocus", world.player), BOHLocation, BOHItem)
            for j in range(1 + 1, 1 + 9):
                e_next = [a for a in _all_of_path if str(j) in a.IdStr][0]
                l.remove(e_next)
                wt.add_event("__event_" + e_next.IdStr, "__event_" + e_next.IdStr,
                             lambda state, s="__event_" + e.IdStr: state.has(s, world.player), BOHLocation, BOHItem)
                e = e_next
        assert len(l) == 0
