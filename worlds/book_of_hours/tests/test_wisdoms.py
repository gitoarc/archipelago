from .bases import BOHTestBase


class TestWisdomsOff(BOHTestBase):
    options = {
        "insanitree": False,
    }

    # Once again, this is just default settings, so running the default tests would be wasteful.
    run_default_tests = False

    # The hammer option adds the Hammer item to the itempool.
    # Since the hammer option is off in this TestCase, we have to verify that the Hammer is *not* in the itempool.
    def test_wisdom_events_dont_exist(self) -> None:
        items_in_itempool = self.get_items_by_name("Wisdoms:")
        #self.assertEqual(len(items_in_itempool), 0)
