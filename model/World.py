class World:
    def __init__(self, tick_index, tick_count, width, height, players, new_vehicles, vehicle_updates,
                 terrain_by_cell_x_y, weather_by_cell_x_y, facilities):
        self.tick_index = tick_index
        self.tick_count = tick_count
        self.width = width
        self.height = height
        self.players = players
        self.new_vehicles = new_vehicles
        self.vehicle_updates = vehicle_updates
        self.terrain_by_cell_x_y = terrain_by_cell_x_y
        self.weather_by_cell_x_y = weather_by_cell_x_y
        self.facilities = facilities

    def get_my_player(self):
        for player in self.players:
            if player.me:
                return player

        return None

    def get_opponent_player(self):
        for player in self.players:
            if not player.me:
                return player

        return None
