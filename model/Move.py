class Move:
    def __init__(self):
        self.action = None
        self.group = 0
        self.left = 0.0
        self.top = 0.0
        self.right = 0.0
        self.bottom = 0.0
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.factor = 0.0
        self.max_speed = 0.0
        self.max_angular_speed = 0.0
        self.vehicle_type = None
        self.facility_id = -1
        self.vehicle_id = -1
