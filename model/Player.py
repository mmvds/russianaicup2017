class Player:
    def __init__(self, id, me, strategy_crashed, score, remaining_action_cooldown_ticks,
                 remaining_nuclear_strike_cooldown_ticks, next_nuclear_strike_vehicle_id,
                 next_nuclear_strike_tick_index, next_nuclear_strike_x, next_nuclear_strike_y):
        self.id = id
        self.me = me
        self.strategy_crashed = strategy_crashed
        self.score = score
        self.remaining_action_cooldown_ticks = remaining_action_cooldown_ticks
        self.remaining_nuclear_strike_cooldown_ticks = remaining_nuclear_strike_cooldown_ticks
        self.next_nuclear_strike_vehicle_id = next_nuclear_strike_vehicle_id
        self.next_nuclear_strike_tick_index = next_nuclear_strike_tick_index
        self.next_nuclear_strike_x = next_nuclear_strike_x
        self.next_nuclear_strike_y = next_nuclear_strike_y
