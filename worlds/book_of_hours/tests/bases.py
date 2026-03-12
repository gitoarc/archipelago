from test.bases import WorldTestBase

from ..world import BOHWorld

class BOHTestBase(WorldTestBase):
    game = "Book of Hours"
    world: BOHWorld