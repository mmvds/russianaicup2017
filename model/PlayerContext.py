from model.Player import Player
from model.World import World


class PlayerContext:
    def __init__(self, player: (None, Player), world: (None, World)):
        self.player = player
        self.world = world
