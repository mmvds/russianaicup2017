class Game:
    def __init__(self, random_seed, tick_count, world_width, world_height, fog_of_war_enabled, victory_score,
                 facility_capture_score, vehicle_elimination_score, action_detection_interval, base_action_count,
                 additional_action_count_per_control_center, max_unit_group, terrain_weather_map_column_count,
                 terrain_weather_map_row_count, plain_terrain_vision_factor, plain_terrain_stealth_factor,
                 plain_terrain_speed_factor, swamp_terrain_vision_factor, swamp_terrain_stealth_factor,
                 swamp_terrain_speed_factor, forest_terrain_vision_factor, forest_terrain_stealth_factor,
                 forest_terrain_speed_factor, clear_weather_vision_factor, clear_weather_stealth_factor,
                 clear_weather_speed_factor, cloud_weather_vision_factor, cloud_weather_stealth_factor,
                 cloud_weather_speed_factor, rain_weather_vision_factor, rain_weather_stealth_factor,
                 rain_weather_speed_factor, vehicle_radius, tank_durability, tank_speed, tank_vision_range,
                 tank_ground_attack_range, tank_aerial_attack_range, tank_ground_damage, tank_aerial_damage,
                 tank_ground_defence, tank_aerial_defence, tank_attack_cooldown_ticks, tank_production_cost,
                 ifv_durability, ifv_speed, ifv_vision_range, ifv_ground_attack_range, ifv_aerial_attack_range,
                 ifv_ground_damage, ifv_aerial_damage, ifv_ground_defence, ifv_aerial_defence,
                 ifv_attack_cooldown_ticks, ifv_production_cost, arrv_durability, arrv_speed, arrv_vision_range,
                 arrv_ground_defence, arrv_aerial_defence, arrv_production_cost, arrv_repair_range, arrv_repair_speed,
                 helicopter_durability, helicopter_speed, helicopter_vision_range, helicopter_ground_attack_range,
                 helicopter_aerial_attack_range, helicopter_ground_damage, helicopter_aerial_damage,
                 helicopter_ground_defence, helicopter_aerial_defence, helicopter_attack_cooldown_ticks,
                 helicopter_production_cost, fighter_durability, fighter_speed, fighter_vision_range,
                 fighter_ground_attack_range, fighter_aerial_attack_range, fighter_ground_damage, fighter_aerial_damage,
                 fighter_ground_defence, fighter_aerial_defence, fighter_attack_cooldown_ticks, fighter_production_cost,
                 max_facility_capture_points, facility_capture_points_per_vehicle_per_tick, facility_width,
                 facility_height, base_tactical_nuclear_strike_cooldown,
                 tactical_nuclear_strike_cooldown_decrease_per_control_center, max_tactical_nuclear_strike_damage,
                 tactical_nuclear_strike_radius, tactical_nuclear_strike_delay):
        self.random_seed = random_seed
        self.tick_count = tick_count
        self.world_width = world_width
        self.world_height = world_height
        self.fog_of_war_enabled = fog_of_war_enabled
        self.victory_score = victory_score
        self.facility_capture_score = facility_capture_score
        self.vehicle_elimination_score = vehicle_elimination_score
        self.action_detection_interval = action_detection_interval
        self.base_action_count = base_action_count
        self.additional_action_count_per_control_center = additional_action_count_per_control_center
        self.max_unit_group = max_unit_group
        self.terrain_weather_map_column_count = terrain_weather_map_column_count
        self.terrain_weather_map_row_count = terrain_weather_map_row_count
        self.plain_terrain_vision_factor = plain_terrain_vision_factor
        self.plain_terrain_stealth_factor = plain_terrain_stealth_factor
        self.plain_terrain_speed_factor = plain_terrain_speed_factor
        self.swamp_terrain_vision_factor = swamp_terrain_vision_factor
        self.swamp_terrain_stealth_factor = swamp_terrain_stealth_factor
        self.swamp_terrain_speed_factor = swamp_terrain_speed_factor
        self.forest_terrain_vision_factor = forest_terrain_vision_factor
        self.forest_terrain_stealth_factor = forest_terrain_stealth_factor
        self.forest_terrain_speed_factor = forest_terrain_speed_factor
        self.clear_weather_vision_factor = clear_weather_vision_factor
        self.clear_weather_stealth_factor = clear_weather_stealth_factor
        self.clear_weather_speed_factor = clear_weather_speed_factor
        self.cloud_weather_vision_factor = cloud_weather_vision_factor
        self.cloud_weather_stealth_factor = cloud_weather_stealth_factor
        self.cloud_weather_speed_factor = cloud_weather_speed_factor
        self.rain_weather_vision_factor = rain_weather_vision_factor
        self.rain_weather_stealth_factor = rain_weather_stealth_factor
        self.rain_weather_speed_factor = rain_weather_speed_factor
        self.vehicle_radius = vehicle_radius
        self.tank_durability = tank_durability
        self.tank_speed = tank_speed
        self.tank_vision_range = tank_vision_range
        self.tank_ground_attack_range = tank_ground_attack_range
        self.tank_aerial_attack_range = tank_aerial_attack_range
        self.tank_ground_damage = tank_ground_damage
        self.tank_aerial_damage = tank_aerial_damage
        self.tank_ground_defence = tank_ground_defence
        self.tank_aerial_defence = tank_aerial_defence
        self.tank_attack_cooldown_ticks = tank_attack_cooldown_ticks
        self.tank_production_cost = tank_production_cost
        self.ifv_durability = ifv_durability
        self.ifv_speed = ifv_speed
        self.ifv_vision_range = ifv_vision_range
        self.ifv_ground_attack_range = ifv_ground_attack_range
        self.ifv_aerial_attack_range = ifv_aerial_attack_range
        self.ifv_ground_damage = ifv_ground_damage
        self.ifv_aerial_damage = ifv_aerial_damage
        self.ifv_ground_defence = ifv_ground_defence
        self.ifv_aerial_defence = ifv_aerial_defence
        self.ifv_attack_cooldown_ticks = ifv_attack_cooldown_ticks
        self.ifv_production_cost = ifv_production_cost
        self.arrv_durability = arrv_durability
        self.arrv_speed = arrv_speed
        self.arrv_vision_range = arrv_vision_range
        self.arrv_ground_defence = arrv_ground_defence
        self.arrv_aerial_defence = arrv_aerial_defence
        self.arrv_production_cost = arrv_production_cost
        self.arrv_repair_range = arrv_repair_range
        self.arrv_repair_speed = arrv_repair_speed
        self.helicopter_durability = helicopter_durability
        self.helicopter_speed = helicopter_speed
        self.helicopter_vision_range = helicopter_vision_range
        self.helicopter_ground_attack_range = helicopter_ground_attack_range
        self.helicopter_aerial_attack_range = helicopter_aerial_attack_range
        self.helicopter_ground_damage = helicopter_ground_damage
        self.helicopter_aerial_damage = helicopter_aerial_damage
        self.helicopter_ground_defence = helicopter_ground_defence
        self.helicopter_aerial_defence = helicopter_aerial_defence
        self.helicopter_attack_cooldown_ticks = helicopter_attack_cooldown_ticks
        self.helicopter_production_cost = helicopter_production_cost
        self.fighter_durability = fighter_durability
        self.fighter_speed = fighter_speed
        self.fighter_vision_range = fighter_vision_range
        self.fighter_ground_attack_range = fighter_ground_attack_range
        self.fighter_aerial_attack_range = fighter_aerial_attack_range
        self.fighter_ground_damage = fighter_ground_damage
        self.fighter_aerial_damage = fighter_aerial_damage
        self.fighter_ground_defence = fighter_ground_defence
        self.fighter_aerial_defence = fighter_aerial_defence
        self.fighter_attack_cooldown_ticks = fighter_attack_cooldown_ticks
        self.fighter_production_cost = fighter_production_cost
        self.max_facility_capture_points = max_facility_capture_points
        self.facility_capture_points_per_vehicle_per_tick = facility_capture_points_per_vehicle_per_tick
        self.facility_width = facility_width
        self.facility_height = facility_height
        self.base_tactical_nuclear_strike_cooldown = base_tactical_nuclear_strike_cooldown
        self.tactical_nuclear_strike_cooldown_decrease_per_control_center = tactical_nuclear_strike_cooldown_decrease_per_control_center
        self.max_tactical_nuclear_strike_damage = max_tactical_nuclear_strike_damage
        self.tactical_nuclear_strike_radius = tactical_nuclear_strike_radius
        self.tactical_nuclear_strike_delay = tactical_nuclear_strike_delay
