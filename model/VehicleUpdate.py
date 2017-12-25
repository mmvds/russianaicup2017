class VehicleUpdate:
    def __init__(self, id, x, y, durability, remaining_attack_cooldown_ticks, selected, groups):
        self.id = id
        self.x = x
        self.y = y
        self.durability = durability
        self.remaining_attack_cooldown_ticks = remaining_attack_cooldown_ticks
        self.selected = selected
        self.groups = groups
