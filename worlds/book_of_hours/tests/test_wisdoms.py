from BaseClasses import Location, LocationProgressType
from .bases import BOHTestBase
from ..enums import BOH_StrEnums
from ..functions import int_from_roman_in_wt_node


class TestWisdoms_Off(BOHTestBase):
    options = {
        "insanitree": {
            "from_tier": 0,
            "to_tier": 0,
            "split_paths": 1
        }
    }


class TestWisdoms_0to9_Split(BOHTestBase):
    run_default_tests = False
    options = {
        "insanitree": {
            "from_tier": 0,
            "to_tier": 9,
            "split_paths": 1,
            "location_progress_types": 1232123231,
        }
    }

    def test_len_locations_is_82(self):
        reg = self.world.get_region(BOH_StrEnums.TreeOfWisdoms)
        loc = [a for a in reg.locations]
        self.assertTrue(len(loc) == 1 + 9 * 9,
                        f"expected {1 + 9 * 9} locations, but found {len(loc)}")  # Root node + 9 slots * 9 paths

    def test_loc_types(self):
        assert self.world.options.insanitree.location_progress_types
        reg = self.world.get_region(BOH_StrEnums.TreeOfWisdoms)
        locs:list[Location] = [a for a in reg.locations]
        for i in range(1,10):
            t_locs = [a for a in locs if int_from_roman_in_wt_node(a.name) == i]
            for l in t_locs:
                expected = int(self.world.options.insanitree.location_progress_types[i])
                expected = LocationProgressType(expected)
                self.assertTrue(l.progress_type == expected)
                locs.remove(l)
        [root] = locs
        self.assertTrue(root.progress_type == LocationProgressType(int(self.world.options.insanitree.location_progress_types[0])))
        pass


class TestWisdoms_1to3_Split(BOHTestBase):
    run_default_tests = False
    options = {
        "insanitree": {
            "from_tier": 1,
            "to_tier": 3,
            "split_paths": 1
        }
    }

    def test_len_locations(self):
        reg = self.world.get_region(BOH_StrEnums.TreeOfWisdoms)
        loc = [a for a in reg.locations]
        self.assertTrue(len(loc) == 3 * 9, f"expected {1 * 3 * 9} locations, but found {len(loc)}: {loc}")

class TestWisdoms_0To9_NoSplit(BOHTestBase):
    run_default_tests = False
    options = {
        "insanitree": {
            "from_tier": 0,
            "to_tier": 9,
            "split_paths": 0
        }
    }
    def test_len_locations_is_10(self):
        reg = self.world.get_region(BOH_StrEnums.TreeOfWisdoms)
        loc:list = [a for a in reg.locations]
        self.assertTrue(len(loc) == 10, f"expected 10 locations, but found {len(loc)}: {loc}")
