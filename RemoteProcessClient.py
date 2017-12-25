import io
import socket
import struct

from model.Facility import Facility
from model.FacilityType import FacilityType
from model.Game import Game
from model.Player import Player
from model.PlayerContext import PlayerContext
from model.TerrainType import TerrainType
from model.Vehicle import Vehicle
from model.VehicleType import VehicleType
from model.VehicleUpdate import VehicleUpdate
from model.WeatherType import WeatherType
from model.World import World


class RemoteProcessClient:
    BUFFER_SIZE_BYTES = 1 << 20
    LITTLE_ENDIAN_BYTE_ORDER = True
    BYTE_ORDER_FORMAT_STRING = "<" if LITTLE_ENDIAN_BYTE_ORDER else ">"

    BYTE_FORMAT_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "b")
    INT_FORMAT_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "i")
    LONG_FORMAT_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "q")
    DOUBLE_FORMAT_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "d")

    INTEGER_SIZE_BYTES = 4
    LONG_SIZE_BYTES = 8
    DOUBLE_SIZE_BYTES = 8

    GAME_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "qi2db9i19di4d7i4d7i2d3i2di4d7i4d6i4d2i2di")
    PLAYER_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "q2b3iqi2d")
    VEHICLE_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "q3dq2i7d6i")
    VEHICLE_UPDATE_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "q2d2ib")
    WORLD_STRUCT = struct.Struct(BYTE_ORDER_FORMAT_STRING + "2i2d")

    def __init__(self, host, port):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.socket.connect((host, port))
        self.buffered_reader = io.BufferedReader(socket.SocketIO(self.socket, 'rb'))

        self.previous_players = None
        self.previous_player_by_id = {}
        self.previous_facilities = None
        self.previous_facility_by_id = {}
        self.terrain_by_cell_x_y = None
        self.weather_by_cell_x_y = None

    def write_token_message(self, token):
        self.write_enum(RemoteProcessClient.MessageType.AUTHENTICATION_TOKEN)
        self.write_string(token)

    def write_protocol_version_message(self):
        self.write_enum(RemoteProcessClient.MessageType.PROTOCOL_VERSION)
        self.write_int(3)

    def read_team_size_message(self):
        message_type = self.read_enum(RemoteProcessClient.MessageType)
        self.ensure_message_type(message_type, RemoteProcessClient.MessageType.TEAM_SIZE)
        self.read_int()

    def read_game_context_message(self):
        message_type = self.read_enum(RemoteProcessClient.MessageType)
        self.ensure_message_type(message_type, RemoteProcessClient.MessageType.GAME_CONTEXT)
        return self.read_game()

    def read_player_context_message(self):
        message_type = self.read_enum(RemoteProcessClient.MessageType)
        if message_type == RemoteProcessClient.MessageType.GAME_OVER:
            return None

        self.ensure_message_type(message_type, RemoteProcessClient.MessageType.PLAYER_CONTEXT)
        return self.read_player_context()

    def write_move_message(self, move):
        self.write_enum(RemoteProcessClient.MessageType.MOVE)
        self.write_move(move)

    def close(self):
        self.socket.close()

    def read_facility(self):
        flag = self.read_signed_byte()

        if flag == 0:
            return None

        if flag == 127:
            return self.previous_facility_by_id[self.read_long()]

        facility = Facility(
            self.read_long(), self.read_enum(FacilityType), self.read_long(), self.read_double(), self.read_double(),
            self.read_double(), self.read_enum(VehicleType), self.read_int()
        )
        self.previous_facility_by_id[facility.id] = facility
        return facility

    def write_facility(self, facility):
        if facility is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_long(facility.id)
            self.write_enum(facility.type)
            self.write_long(facility.owner_player_id)
            self.write_double(facility.left)
            self.write_double(facility.top)
            self.write_double(facility.capture_points)
            self.write_enum(facility.vehicle_type)
            self.write_int(facility.production_progress)

    def read_facilities(self):
        facility_count = self.read_int()
        if facility_count < 0:
            return self.previous_facilities

        facilities = [self.read_facility() for _ in range(facility_count)]
        self.previous_facilities = facilities
        return facilities

    def write_facilities(self, facilities):
        if facilities is None:
            self.write_int(-1)
        else:
            self.write_int(facilities.__len__())

            for facility in facilities:
                self.write_facility(facility)

    def read_game(self):
        if not self.read_boolean():
            return None

        byte_array = self.read_bytes(565)
        game = RemoteProcessClient.GAME_STRUCT.unpack(byte_array)

        return Game(
            game[0], game[1], game[2], game[3], game[4] != 0, game[5], game[6], game[7], game[8], game[9], game[10],
            game[11], game[12], game[13], game[14], game[15], game[16], game[17], game[18], game[19], game[20],
            game[21], game[22], game[23], game[24], game[25], game[26], game[27], game[28], game[29], game[30],
            game[31], game[32], game[33], game[34], game[35], game[36], game[37], game[38], game[39], game[40],
            game[41], game[42], game[43], game[44], game[45], game[46], game[47], game[48], game[49], game[50],
            game[51], game[52], game[53], game[54], game[55], game[56], game[57], game[58], game[59], game[60],
            game[61], game[62], game[63], game[64], game[65], game[66], game[67], game[68], game[69], game[70],
            game[71], game[72], game[73], game[74], game[75], game[76], game[77], game[78], game[79], game[80],
            game[81], game[82], game[83], game[84], game[85], game[86], game[87], game[88], game[89], game[90],
            game[91], game[92], game[93]
        )

    def write_game(self, game):
        if game is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_long(game.random_seed)
            self.write_int(game.tick_count)
            self.write_double(game.world_width)
            self.write_double(game.world_height)
            self.write_boolean(game.fog_of_war_enabled)
            self.write_int(game.victory_score)
            self.write_int(game.facility_capture_score)
            self.write_int(game.vehicle_elimination_score)
            self.write_int(game.action_detection_interval)
            self.write_int(game.base_action_count)
            self.write_int(game.additional_action_count_per_control_center)
            self.write_int(game.max_unit_group)
            self.write_int(game.terrain_weather_map_column_count)
            self.write_int(game.terrain_weather_map_row_count)
            self.write_double(game.plain_terrain_vision_factor)
            self.write_double(game.plain_terrain_stealth_factor)
            self.write_double(game.plain_terrain_speed_factor)
            self.write_double(game.swamp_terrain_vision_factor)
            self.write_double(game.swamp_terrain_stealth_factor)
            self.write_double(game.swamp_terrain_speed_factor)
            self.write_double(game.forest_terrain_vision_factor)
            self.write_double(game.forest_terrain_stealth_factor)
            self.write_double(game.forest_terrain_speed_factor)
            self.write_double(game.clear_weather_vision_factor)
            self.write_double(game.clear_weather_stealth_factor)
            self.write_double(game.clear_weather_speed_factor)
            self.write_double(game.cloud_weather_vision_factor)
            self.write_double(game.cloud_weather_stealth_factor)
            self.write_double(game.cloud_weather_speed_factor)
            self.write_double(game.rain_weather_vision_factor)
            self.write_double(game.rain_weather_stealth_factor)
            self.write_double(game.rain_weather_speed_factor)
            self.write_double(game.vehicle_radius)
            self.write_int(game.tank_durability)
            self.write_double(game.tank_speed)
            self.write_double(game.tank_vision_range)
            self.write_double(game.tank_ground_attack_range)
            self.write_double(game.tank_aerial_attack_range)
            self.write_int(game.tank_ground_damage)
            self.write_int(game.tank_aerial_damage)
            self.write_int(game.tank_ground_defence)
            self.write_int(game.tank_aerial_defence)
            self.write_int(game.tank_attack_cooldown_ticks)
            self.write_int(game.tank_production_cost)
            self.write_int(game.ifv_durability)
            self.write_double(game.ifv_speed)
            self.write_double(game.ifv_vision_range)
            self.write_double(game.ifv_ground_attack_range)
            self.write_double(game.ifv_aerial_attack_range)
            self.write_int(game.ifv_ground_damage)
            self.write_int(game.ifv_aerial_damage)
            self.write_int(game.ifv_ground_defence)
            self.write_int(game.ifv_aerial_defence)
            self.write_int(game.ifv_attack_cooldown_ticks)
            self.write_int(game.ifv_production_cost)
            self.write_int(game.arrv_durability)
            self.write_double(game.arrv_speed)
            self.write_double(game.arrv_vision_range)
            self.write_int(game.arrv_ground_defence)
            self.write_int(game.arrv_aerial_defence)
            self.write_int(game.arrv_production_cost)
            self.write_double(game.arrv_repair_range)
            self.write_double(game.arrv_repair_speed)
            self.write_int(game.helicopter_durability)
            self.write_double(game.helicopter_speed)
            self.write_double(game.helicopter_vision_range)
            self.write_double(game.helicopter_ground_attack_range)
            self.write_double(game.helicopter_aerial_attack_range)
            self.write_int(game.helicopter_ground_damage)
            self.write_int(game.helicopter_aerial_damage)
            self.write_int(game.helicopter_ground_defence)
            self.write_int(game.helicopter_aerial_defence)
            self.write_int(game.helicopter_attack_cooldown_ticks)
            self.write_int(game.helicopter_production_cost)
            self.write_int(game.fighter_durability)
            self.write_double(game.fighter_speed)
            self.write_double(game.fighter_vision_range)
            self.write_double(game.fighter_ground_attack_range)
            self.write_double(game.fighter_aerial_attack_range)
            self.write_int(game.fighter_ground_damage)
            self.write_int(game.fighter_aerial_damage)
            self.write_int(game.fighter_ground_defence)
            self.write_int(game.fighter_aerial_defence)
            self.write_int(game.fighter_attack_cooldown_ticks)
            self.write_int(game.fighter_production_cost)
            self.write_double(game.max_facility_capture_points)
            self.write_double(game.facility_capture_points_per_vehicle_per_tick)
            self.write_double(game.facility_width)
            self.write_double(game.facility_height)
            self.write_int(game.base_tactical_nuclear_strike_cooldown)
            self.write_int(game.tactical_nuclear_strike_cooldown_decrease_per_control_center)
            self.write_double(game.max_tactical_nuclear_strike_damage)
            self.write_double(game.tactical_nuclear_strike_radius)
            self.write_int(game.tactical_nuclear_strike_delay)

    def read_games(self):
        game_count = self.read_int()
        if game_count < 0:
            return None

        return [self.read_game() for _ in range(game_count)]

    def write_games(self, games):
        if games is None:
            self.write_int(-1)
        else:
            self.write_int(games.__len__())

            for game in games:
                self.write_game(game)

    def write_move(self, move):
        if move is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_enum(move.action)
            self.write_int(move.group)
            self.write_double(move.left)
            self.write_double(move.top)
            self.write_double(move.right)
            self.write_double(move.bottom)
            self.write_double(move.x)
            self.write_double(move.y)
            self.write_double(move.angle)
            self.write_double(move.factor)
            self.write_double(move.max_speed)
            self.write_double(move.max_angular_speed)
            self.write_enum(move.vehicle_type)
            self.write_long(move.facility_id)
            self.write_long(move.vehicle_id)

    def write_moves(self, moves):
        if moves is None:
            self.write_int(-1)
        else:
            self.write_int(moves.__len__())

            for move in moves:
                self.write_move(move)

    def read_player(self):
        flag = self.read_signed_byte()

        if flag == 0:
            return None

        if flag == 127:
            return self.previous_player_by_id[self.read_long()]

        byte_array = self.read_bytes(50)
        player = RemoteProcessClient.PLAYER_STRUCT.unpack(byte_array)

        player = Player(
            player[0], player[1] != 0, player[2] != 0, player[3], player[4], player[5], player[6], player[7], player[8],
            player[9]
        )
        self.previous_player_by_id[player.id] = player
        return player

    def write_player(self, player):
        if player is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_long(player.id)
            self.write_boolean(player.me)
            self.write_boolean(player.strategy_crashed)
            self.write_int(player.score)
            self.write_int(player.remaining_action_cooldown_ticks)
            self.write_int(player.remaining_nuclear_strike_cooldown_ticks)
            self.write_long(player.next_nuclear_strike_vehicle_id)
            self.write_int(player.next_nuclear_strike_tick_index)
            self.write_double(player.next_nuclear_strike_x)
            self.write_double(player.next_nuclear_strike_y)

    def read_players(self):
        player_count = self.read_int()
        if player_count < 0:
            return self.previous_players

        players = [self.read_player() for _ in range(player_count)]
        self.previous_players = players
        return players

    def write_players(self, players):
        if players is None:
            self.write_int(-1)
        else:
            self.write_int(players.__len__())

            for player in players:
                self.write_player(player)

    def read_player_context(self):
        if not self.read_boolean():
            return None

        return PlayerContext(self.read_player(), self.read_world())

    def write_player_context(self, player_context):
        if player_context is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_player(player_context.player)
            self.write_world(player_context.world)

    def read_player_contexts(self):
        player_context_count = self.read_int()
        if player_context_count < 0:
            return None

        return [self.read_player_context() for _ in range(player_context_count)]

    def write_player_contexts(self, player_contexts):
        if player_contexts is None:
            self.write_int(-1)
        else:
            self.write_int(player_contexts.__len__())

            for player_context in player_contexts:
                self.write_player_context(player_context)

    def read_vehicle(self):
        if not self.read_boolean():
            return None

        byte_array = self.read_bytes(128)
        vehicle = RemoteProcessClient.VEHICLE_STRUCT.unpack(byte_array)

        return Vehicle(
            vehicle[0], vehicle[1], vehicle[2], vehicle[3], vehicle[4], vehicle[5], vehicle[6], vehicle[7], vehicle[8],
            vehicle[9], vehicle[10], vehicle[11], vehicle[12], vehicle[13], vehicle[14], vehicle[15], vehicle[16],
            vehicle[17], vehicle[18], vehicle[19], self.read_enum(VehicleType), self.read_boolean(),
            self.read_boolean(), self.read_ints()
        )

    def write_vehicle(self, vehicle):
        if vehicle is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_long(vehicle.id)
            self.write_double(vehicle.x)
            self.write_double(vehicle.y)
            self.write_double(vehicle.radius)
            self.write_long(vehicle.player_id)
            self.write_int(vehicle.durability)
            self.write_int(vehicle.max_durability)
            self.write_double(vehicle.max_speed)
            self.write_double(vehicle.vision_range)
            self.write_double(vehicle.squared_vision_range)
            self.write_double(vehicle.ground_attack_range)
            self.write_double(vehicle.squared_ground_attack_range)
            self.write_double(vehicle.aerial_attack_range)
            self.write_double(vehicle.squared_aerial_attack_range)
            self.write_int(vehicle.ground_damage)
            self.write_int(vehicle.aerial_damage)
            self.write_int(vehicle.ground_defence)
            self.write_int(vehicle.aerial_defence)
            self.write_int(vehicle.attack_cooldown_ticks)
            self.write_int(vehicle.remaining_attack_cooldown_ticks)
            self.write_enum(vehicle.type)
            self.write_boolean(vehicle.aerial)
            self.write_boolean(vehicle.selected)
            self.write_ints(vehicle.groups)

    def read_vehicles(self):
        vehicle_count = self.read_int()
        if vehicle_count < 0:
            return None

        return [self.read_vehicle() for _ in range(vehicle_count)]

    def write_vehicles(self, vehicles):
        if vehicles is None:
            self.write_int(-1)
        else:
            self.write_int(vehicles.__len__())

            for vehicle in vehicles:
                self.write_vehicle(vehicle)

    def read_vehicle_update(self):
        if not self.read_boolean():
            return None

        byte_array = self.read_bytes(33)
        vehicle_update = RemoteProcessClient.VEHICLE_UPDATE_STRUCT.unpack(byte_array)

        return VehicleUpdate(
            vehicle_update[0], vehicle_update[1], vehicle_update[2], vehicle_update[3], vehicle_update[4],
            vehicle_update[5] != 0, self.read_ints()
        )

    def write_vehicle_update(self, vehicle_update):
        if vehicle_update is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_long(vehicle_update.id)
            self.write_double(vehicle_update.x)
            self.write_double(vehicle_update.y)
            self.write_int(vehicle_update.durability)
            self.write_int(vehicle_update.remaining_attack_cooldown_ticks)
            self.write_boolean(vehicle_update.selected)
            self.write_ints(vehicle_update.groups)

    def read_vehicle_updates(self):
        vehicle_update_count = self.read_int()
        if vehicle_update_count < 0:
            return None

        return [self.read_vehicle_update() for _ in range(vehicle_update_count)]

    def write_vehicle_updates(self, vehicle_updates):
        if vehicle_updates is None:
            self.write_int(-1)
        else:
            self.write_int(vehicle_updates.__len__())

            for vehicle_update in vehicle_updates:
                self.write_vehicle_update(vehicle_update)

    def read_world(self):
        if not self.read_boolean():
            return None

        byte_array = self.read_bytes(24)
        world = RemoteProcessClient.WORLD_STRUCT.unpack(byte_array)

        return World(
            world[0], world[1], world[2], world[3], self.read_players(), self.read_vehicles(),
            self.read_vehicle_updates(), self.read_terrain_by_cell_x_y(), self.read_weather_by_cell_x_y(),
            self.read_facilities()
        )

    def write_world(self, world):
        if world is None:
            self.write_boolean(False)
        else:
            self.write_boolean(True)

            self.write_int(world.tick_index)
            self.write_int(world.tick_count)
            self.write_double(world.width)
            self.write_double(world.height)
            self.write_players(world.players)
            self.write_vehicles(world.new_vehicles)
            self.write_vehicle_updates(world.vehicle_updates)
            self.write_enums_2d(world.terrain_by_cell_x_y)
            self.write_enums_2d(world.weather_by_cell_x_y)
            self.write_facilities(world.facilities)

    def read_worlds(self):
        world_count = self.read_int()
        if world_count < 0:
            return None

        return [self.read_world() for _ in range(world_count)]

    def write_worlds(self, worlds):
        if worlds is None:
            self.write_int(-1)
        else:
            self.write_int(worlds.__len__())

            for world in worlds:
                self.write_world(world)

    def read_terrain_by_cell_x_y(self):
        if self.terrain_by_cell_x_y is None:
            self.terrain_by_cell_x_y = self.read_enums_2d(TerrainType)

        return self.terrain_by_cell_x_y

    def read_weather_by_cell_x_y(self):
        if self.weather_by_cell_x_y is None:
            self.weather_by_cell_x_y = self.read_enums_2d(WeatherType)

        return self.weather_by_cell_x_y

    @staticmethod
    def ensure_message_type(actual_type, expected_type):
        if actual_type != expected_type:
            raise ValueError("Received wrong message [actual=%s, expected=%s]." % (actual_type, expected_type))

    def read_enum(self, enum_class):
        byte_array = self.read_bytes(1)
        value = RemoteProcessClient.BYTE_FORMAT_STRUCT.unpack(byte_array)[0]

        for enum_key, enum_value in enum_class.__dict__.items():
            if not str(enum_key).startswith("__") and value == enum_value:
                return enum_value

        return None

    def read_byte_array(self, nullable):
        count = self.read_int()

        if count <= 0:
            return None if nullable and count < 0 else bytes()

        return self.read_bytes(count)

    def write_byte_array(self, array):
        if array is None:
            self.write_int(-1)
        else:
            self.write_int(array.__len__())
            self.write_bytes(array)

    def read_enums(self, enum_class):
        count = self.read_int()
        return None if count < 0 else [self.read_enum(enum_class) for _ in range(count)]

    def read_enums_2d(self, enum_class):
        count = self.read_int()
        return None if count < 0 else [self.read_enums(enum_class) for _ in range(count)]

    def write_enum(self, value):
        self.write_bytes(RemoteProcessClient.BYTE_FORMAT_STRUCT.pack(-1 if value is None else value))

    def write_enums(self, enums):
        if enums is None:
            self.write_int(-1)
        else:
            self.write_int(enums.__len__())

            for value in enums:
                self.write_enum(value)

    def write_enums_2d(self, enums_2d):
        if enums_2d is None:
            self.write_int(-1)
        else:
            self.write_int(enums_2d.__len__())

            for enums in enums_2d:
                self.write_enums(enums)

    def read_string(self):
        length = self.read_int()
        if length == -1:
            return None

        byte_array = self.read_bytes(length)
        return byte_array.decode()

    def write_string(self, value):
        if value is None:
            self.write_int(-1)
            return

        byte_array = value.encode()

        self.write_int(len(byte_array))
        self.write_bytes(byte_array)

    def read_signed_byte(self):
        byte_array = self.read_bytes(1)
        return RemoteProcessClient.BYTE_FORMAT_STRUCT.unpack(byte_array)[0]

    def read_boolean(self):
        return self.read_bytes(1) != b'\0'

    def read_boolean_array(self, count):
        byte_array = self.read_bytes(count)
        unpacked_bytes = struct.unpack(RemoteProcessClient.BYTE_ORDER_FORMAT_STRING + str(count) + "b", byte_array)

        return [unpacked_bytes[i] != 0 for i in range(count)]

    def write_boolean(self, value):
        self.write_bytes(RemoteProcessClient.BYTE_FORMAT_STRUCT.pack(1 if value else 0))

    def read_int(self):
        byte_array = self.read_bytes(RemoteProcessClient.INTEGER_SIZE_BYTES)
        return RemoteProcessClient.INT_FORMAT_STRUCT.unpack(byte_array)[0]

    def read_ints(self):
        count = self.read_int()
        if count < 0:
            return None

        ints = []

        if count > 0:
            byte_array = self.read_bytes(RemoteProcessClient.INTEGER_SIZE_BYTES * count)
            ints.extend(struct.unpack(RemoteProcessClient.BYTE_ORDER_FORMAT_STRING + str(count) + "i", byte_array))

        return ints

    def read_ints_2d(self):
        count = self.read_int()
        return None if count < 0 else [self.read_ints() for _ in range(count)]

    def write_int(self, value):
        self.write_bytes(RemoteProcessClient.INT_FORMAT_STRUCT.pack(value))

    def write_ints(self, ints):
        if ints is None:
            self.write_int(-1)
        else:
            self.write_int(ints.__len__())

            for value in ints:
                self.write_int(value)

    def write_ints_2d(self, ints_2d):
        if ints_2d is None:
            self.write_int(-1)
        else:
            self.write_int(ints_2d.__len__())

            for ints in ints_2d:
                self.write_ints(ints)

    def read_long(self):
        byte_array = self.read_bytes(RemoteProcessClient.LONG_SIZE_BYTES)
        return RemoteProcessClient.LONG_FORMAT_STRUCT.unpack(byte_array)[0]

    def write_long(self, value):
        self.write_bytes(RemoteProcessClient.LONG_FORMAT_STRUCT.pack(value))

    def read_double(self):
        byte_array = self.read_bytes(RemoteProcessClient.DOUBLE_SIZE_BYTES)
        return RemoteProcessClient.DOUBLE_FORMAT_STRUCT.unpack(byte_array)[0]

    def write_double(self, value):
        self.write_bytes(RemoteProcessClient.DOUBLE_FORMAT_STRUCT.pack(value))

    def read_bytes(self, byte_count):
        return self.buffered_reader.read(byte_count)

    def write_bytes(self, byte_array):
        self.socket.sendall(byte_array)

    class MessageType:
        UNKNOWN = 0
        GAME_OVER = 1
        AUTHENTICATION_TOKEN = 2
        TEAM_SIZE = 3
        PROTOCOL_VERSION = 4
        GAME_CONTEXT = 5
        PLAYER_CONTEXT = 6
        MOVE = 7
