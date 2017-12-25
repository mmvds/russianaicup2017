from model.CircularUnit import CircularUnit
from model.VehicleType import VehicleType
from model.VehicleUpdate import VehicleUpdate


class Vehicle(CircularUnit):
    def __init__(self, id, x, y, radius, player_id, durability, max_durability, max_speed, vision_range,
                 squared_vision_range, ground_attack_range, squared_ground_attack_range, aerial_attack_range,
                 squared_aerial_attack_range, ground_damage, aerial_damage, ground_defence, aerial_defence,
                 attack_cooldown_ticks, remaining_attack_cooldown_ticks, type: (None, VehicleType), aerial, selected,
                 groups):
        CircularUnit.__init__(self, id, x, y, radius)

        self.player_id = player_id
        self.durability = durability
        self.max_durability = max_durability
        self.max_speed = max_speed
        self.vision_range = vision_range
        self.squared_vision_range = squared_vision_range
        self.ground_attack_range = ground_attack_range
        self.squared_ground_attack_range = squared_ground_attack_range
        self.aerial_attack_range = aerial_attack_range
        self.squared_aerial_attack_range = squared_aerial_attack_range
        self.ground_damage = ground_damage
        self.aerial_damage = aerial_damage
        self.ground_defence = ground_defence
        self.aerial_defence = aerial_defence
        self.attack_cooldown_ticks = attack_cooldown_ticks
        self.remaining_attack_cooldown_ticks = remaining_attack_cooldown_ticks
        self.type = type
        self.aerial = aerial
        self.selected = selected
        self.groups = groups

    def update(self, vehicle_update: VehicleUpdate):
        if self.id != vehicle_update.id:
            raise ValueError("Vehicle ID mismatch [actual=%s, expected=%s]." % (vehicle_update.id, self.id))

        self.x = vehicle_update.x
        self.y = vehicle_update.y
        self.durability = vehicle_update.durability
        self.remaining_attack_cooldown_ticks = vehicle_update.remaining_attack_cooldown_ticks
        self.selected = vehicle_update.selected
        self.groups = vehicle_update.groups
