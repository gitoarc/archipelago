from __future__ import annotations

from typing import TYPE_CHECKING
from enum import StrEnum, unique
from BaseClasses import Item, ItemClassification
from ._generate_locations import MEMORIES_SPECIFIC
from .functions import predicate_with
from .jsondump import memories, SimplePredicate, lessons

if TYPE_CHECKING:
    from .world import BOHWorld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# ! Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    "Hush House Key": 102,
    "Twopence": 202
}
MEMORIES_NAME_TO_ID = {m.Label: v
                       for m in memories
                       for k, v in MEMORIES_SPECIFIC.items()
                       if m.Label in k}
# make lessons part of memories (bc they are) but also, they have kinda weak existence for being their own category
LESSONS = {o.Label:f"60{i}" for i, o in enumerate(lessons)}
MEMORIES_NAME_TO_ID = MEMORIES_NAME_TO_ID | LESSONS
#LOCATION_AS_EVENT_ITEM = {e.Label: None for e in terrains}


DEFAULT_ITEM_CLASSIFICATIONS = {
    "Hush House Key": ItemClassification.progression | ItemClassification.useful,
    "Twopence": ItemClassification.filler
}
MEMORIES_DEFAULT_CLASSIFICATIONS = {a.Label: ItemClassification.filler for a in memories} # since filler is 0, literally any flag overwrites it
MEMORIES_DEFAULT_CLASSIFICATIONS = MEMORIES_DEFAULT_CLASSIFICATIONS | {a.Label: ItemClassification.filler for a in lessons}
#LOCATION_AS_EVENT_ITEM_CLASSIFICATION = { e.Label: ItemClassification.progression for e in terrains}

# amalgamate every sub-dict togethaa
ITEM_NAME_TO_ID = ITEM_NAME_TO_ID | MEMORIES_NAME_TO_ID
ITEM_CLASSIFICATIONS = DEFAULT_ITEM_CLASSIFICATIONS | MEMORIES_DEFAULT_CLASSIFICATIONS


class BOHItem(Item):
    game = "Book of Hours"


# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: BOHWorld) -> str:
    # IMPORTANT: Whenever you need to use a random generator, you must use world.random.
    # This ensures that generating with the same generator seed twice yields the same output.
    # DO NOT use a bare random object from Python's built-in random module.
    chance_roll = world.random.randint(0,100)

    fillers_and_traps = [k for k,v in ITEM_CLASSIFICATIONS.items() if not v & ItemClassification.progression and not v & ItemClassification.useful]
    traps_only = [k for k,v in ITEM_CLASSIFICATIONS.items() if v & ItemClassification.trap]
    index_roll_fillers_and_traps = world.random.randint(0, len(fillers_and_traps)-1)
    index_roll_traps = world.random.randint(0, len(traps_only)-1)

    chosen_item_name = fillers_and_traps[index_roll_fillers_and_traps]
    # find out what kind of item and apply its trap_chance
    if chosen_item_name in [a.Label for a in memories+lessons] and chance_roll < world.options.memory_items.trap_chance:
        chosen_item_name = traps_only[index_roll_traps]
    pass

    return chosen_item_name


def create_item_with_auto_classification(world: BOHWorld, name: str) -> BOHItem:
    classification = ITEM_CLASSIFICATIONS[name]

    # yes this will run every call; yes its shitty; yes it has to be this way bc the lookups are already passed to world before any def() runs here
    is_memory = any([a for a in memories if a.Label == name])
    if world.options.memory_items.is_enabled and is_memory:
        for k, v in world.options.memory_items.predicates.items():
            categ = v
            match categ:
                case "progression":
                    categ = ItemClassification.progression
                case "trap":
                    categ = ItemClassification.trap
                case _:
                    categ = ItemClassification.filler
            items_to_mod = predicate_with(k)
            if name in [a.Label for a in items_to_mod]:
                ITEM_CLASSIFICATIONS[name] = categ
                classification = categ

    code = ITEM_NAME_TO_ID[name]
    if code is None:
        assert classification & ItemClassification.progression == 1

    return BOHItem(name, classification, code, world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: BOHWorld) -> None:
    # Add unique / "can only drop once" items
    itempool = [world.create_item(k) for k, v in ITEM_NAME_TO_ID.items() if v is not None]
    itempool = [a for a in itempool if not a.trap and not a.filler]

    # Archipelago requires that each world submits as many locations as it submits items.
    # This is where we can use our filler and trap items.
    # APQuest has two of these: The Confetti Cannon and the Math Trap.
    # (Unfortunately, Archipelago is a bit ambiguous about its terminology here:
    #  "filler" is an ItemClassification separate from "trap", but in a lot of its functions,
    #  Archipelago will use "filler" to just mean "an additional item created to fill out the itempool".
    #  "Filler" in this sense can technically have any ItemClassification,
    #  but most commonly ItemClassification.filler or ItemClassification.trap.
    #  Starting here, the word "filler" will be used to collectively refer to APQuest's Confetti Cannon and Math Trap,
    #  which are ItemClassification.filler and ItemClassification.trap respectively.)
    # Creating filler items works the same as any other item. But there is a question:
    # How many filler items do we actually need to create?
    # In regions.py, we created either six or seven locations depending on the "extra_starting_chest" option.
    # In this function, we have created five or six items depending on whether the "hammer" option is enabled.
    # We *could* have a really complicated if-else tree checking the options again, but there is a better way.
    # We can compare the size of our itempool so far to the number of locations in our world.

    # The length of our itempool is easy to determine, since we have it as a list.
    number_of_items = len(itempool)

    # The number of locations is also easy to determine, but we have to be careful.
    # Just calling len(world.get_locations()) would report an incorrect number, because of our *event locations*.
    # What we actually want is the number of *unfilled* locations. Luckily, there is a helper method for this:
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    # Now, we just subtract the number of items from the number of locations to get the number of empty item slots.
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items

    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
