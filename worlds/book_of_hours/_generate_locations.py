from __future__ import annotations

import random

from . import jsondump
from .functions import slice_off_category_from_int, starts_vowel


def __process_label_memory(s: str):
    s = s.replace("Memory: ", "")
    # if vowel: 'a' or 'an'
    matches = ["a", "e", "i", "o", "u"]
    f = s[0:1].lower()
    if any([a in f for a in matches]):
        s = "an " + s
    else:
        s = "a " + s
    return s


def __process_label_soul(s: str):
    return f"a Part: {s}"


def __process_label_lesson(s: str):
    #no access to world.random ... ¯\_(ツ)_/¯
    s = s.replace("Lesson:", "")
    s = random.choice(["of", "in", "about"]) + s
    return s


def __last_subid_of(d: dict[any, int]):
    i = max(d.values())
    i = slice_off_category_from_int(i)
    return i


#################
MEMORIES_SPECIFIC = {f"Remember an {o.Label}" if starts_vowel(o.Label) else f"Remember a {o.Label}"
                     : int(f"10{i + 1}")
                     for i, o in enumerate(jsondump.memories)}
# I would've liked to create these dependant on the options, BUT location_name_to_id IS STATIC -> even generate_early is too late, this HAS to be set before AP calls BoHWorld, but then I don't have the option values...
#MEMORIES_PILE = {f"Remember {x} memories - Reward {y}"
#                 : int(f"10{__last_subid_of(MEMORIES_SPECIFIC) + 1+i}")
#                 for i, (x, y) in enumerate([(a, b) for a in range(1, 1 + 333) for b in range(1, 1 + 3)])
#                 }
MEMORIES_PILE = {f"Remember {m} memories"
                 : int(f"10{__last_subid_of(MEMORIES_SPECIFIC) + m}")
                 for m in range(1, 1 + 333)}
##############
SOULS_SPECIFIC = {f"Acquire {o.Label}": int(f"20{i + 1}")
                  for i, o in enumerate(jsondump.souls)}
SOULS_TIERS = {
    f"Acquire a {"+" * (n + 1)}Soul - Reward {r + 1}": int(f"20{__last_subid_of(SOULS_SPECIFIC) + n * 3 + r}")
    for n in range(0, 3) for r in range(1, 1 + 3)}
SOULS_PILE = {f"Acquire {i} part of the human soul" if i == 1 else f"Acquire {i} parts of the human soul"
              : int(f"20{__last_subid_of(SOULS_TIERS) + i}")
              for i in range(1, 1 + 36)}
#################
TERRAINS_SPECIFIC = {f"Unlock the {o.Label}": int(f"30{i + 1}")
                     for i, o in enumerate(jsondump.terrains)}
TERRAINS_PILE = {f"Unlock {i} terrain" if i == 1 else f"Unlock {i} terrains"
                 : int(f"30{__last_subid_of(TERRAINS_SPECIFIC) + i}")
                 for i in range(1, 111)}  # 110 bc ocean doesnt count
################
WISDOMS_SPECIFIC = {(
    f"Root your Journal into The Tree of Wisdoms" if "Root" in o.Label else f"Commit a skill to '{o.Label}' in The Tree of Wisdoms"): int(
    f"40{i + 1}")
    for i, o in enumerate(jsondump.wisdomtree)}
WISDOMS_TIERS = {f"Reach Tier {t + 1} in The Tree of Wisdoms - Reward {r}"
                 : int(f"40{__last_subid_of(WISDOMS_SPECIFIC) + t * 9 + r}")
                 for t in range(0, 9) for r in range(1,
                                                     1 + 9)}  # this allows more control over the distribution; You could shift the whole tree down to just T2 rewards but 4 items each.
WISDOMS_PILE = {
    f"Commit {n + 1} skill to The Tree of Wisdoms - Reward {r}" if n == 0 else f"Commit {n + 1} skills to The Tree of Wisdoms - Reward {r}"
    : int(f"40{__last_subid_of(WISDOMS_TIERS) + n * 2 + r}")
    for n in range(0, 81) for r in range(1, 1 + 2)}  # a 81*9 combo might be too much? For now, limit to max 2
##############
BOOKS_SPECIFIC = {f"Master '{o.Label}'": int(f"50{i + 1}")
                  for i, o in enumerate(jsondump.books)}
BOOKS_PILE = {f"Master {i} book" if i == 1 else f"Master {i} books"
              : int(f"50{__last_subid_of(BOOKS_SPECIFIC) + i}")
              for i in range(1, 1 + 281)}
###
CATALOG_PILE_ANY = {f"Catalogue {i} book" if i == 1 else f"Catalogue {i} books"
                    : int(f"50{__last_subid_of(BOOKS_PILE) + i}")
                    for i in range(1, 1 + 281)}
CATALOG_PILE_DAWN = {f"Catalogue {i} book of the Dawn Period" if i == 1 else f"Catalogue {i} books of the Dawn Period"
                     : int(f"50{__last_subid_of(CATALOG_PILE_ANY) + i}")
                     for i in range(1, 1 + 60)}
CATALOG_PILE_SOLAR = {
    f"Catalogue {i} book of the Solar Period" if i == 1 else f"Catalogue {i} books of the Solar Period"
    : int(f"50{__last_subid_of(CATALOG_PILE_DAWN) + i}")
    for i in range(1, 1 + 49)}
CATALOG_PILE_BARONIAL = {
    f"Catalogue {i} book of the Baronial Period" if i == 1 else f"Catalogue {i} books of the Baronial Period"
    : int(f"50{__last_subid_of(CATALOG_PILE_SOLAR) + i}")
    for i in range(1, 1 + 60)}
CATALOG_PILE_CURIA = {
    f"Catalogue {i} book of the Curia Period" if i == 1 else f"Catalogue {i} books of the Curia Period"
    : int(f"50{__last_subid_of(CATALOG_PILE_BARONIAL) + i}")
    for i in range(1, 1 + 69)}
CATALOG_PILE_NOCTURNAL = {
    f"Catalogue {i} book of the Nocturnal Period" if i == 1 else f"Catalogue {i} books of the Nocturnal Period"
    : int(f"50{__last_subid_of(CATALOG_PILE_CURIA) + i}")
    for i in range(1, 1 + 43)}
################ I think skills are better for locations since you can use lessons as memories:
# If you want a skill location you have to use up the lesson
# ..and since books do/will reward (random) lessons after mastering, it would just be a double location for mastery (in a sense)
#LESSONS_SPECIFIC = {}
#LESSONS_PILE = {}
###############
SKILLS_SPECIFIC = {f"Learn the skill '{o.Label}'": int(f"70{i + 1}")
                   for i, o in enumerate(jsondump.skills)}
SKILLS_PILE = {f"Learn {i} skill" if i == 1 else f"Learn {i} skills"
               : int(f"70{__last_subid_of(SKILLS_SPECIFIC) + i}")
               for i in range(1, 1 + 73)}

pass
