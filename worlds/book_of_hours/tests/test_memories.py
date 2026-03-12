import re

from .bases import BOHTestBase


class TestMemoryProgressionOff(BOHTestBase):
    run_default_tests = False
    options = {
        "memory_progression": {
            "locations": 0
        }
    }

    def test_memory_progression_locations_do_not_exist(self):
        l = [a for a in self.world.get_locations() if re.search("[0-9] memor", a.name)]
        self.assertTrue(len(l) == 0)

class TestMemoryProgressionOn(BOHTestBase):
    run_default_tests = False
    options = {
        "memory_progression": {
            "locations": 40
        }
    }

    def test_40_locations_exist(self):
        l = [a for a in [a for a in (self.world.get_locations())] if re.search("[0-9] memor", a.name)]
        self.assertTrue(len(l) == 40, f"Expected 40, but location count was {len(l)}")

    def test_progressive_collection(self):
        return None
        with self.subTest("Test first memory requires nothing"):
            first_mem = self.world.get_location("__eventRemember 1")
            b = first_mem.can_reach(self.multiworld.state)
            self.assertTrue(b)

        for i in range(2, 1+40):
            with self.subTest(f"Memory {i} requires {i-1} prog_memories"):
                loc = self.world.get_location(f"__eventRemember {i}")
                self.assertFalse(loc.can_reach(self.multiworld.state), f"can_reach was wrongly true")
                self.multiworld.state.add_item("prog_memories", self.player)
                self.assertTrue(loc.can_reach(self.multiworld.state))

class TestMemorInsanity(BOHTestBase):
    run_default_tests = False

    def test_run(self):
        o = self.options
        pass