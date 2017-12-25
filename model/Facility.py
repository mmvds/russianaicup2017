from model.FacilityType import FacilityType
from model.VehicleType import VehicleType


class Facility:
    def __init__(self, id, type: (None, FacilityType), owner_player_id, left, top, capture_points,
                 vehicle_type: (None, VehicleType), production_progress):
        self.id = id
        self.type = type
        self.owner_player_id = owner_player_id
        self.left = left
        self.top = top
        self.capture_points = capture_points
        self.vehicle_type = vehicle_type
        self.production_progress = production_progress
