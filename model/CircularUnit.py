from model.Unit import Unit


class CircularUnit(Unit):
    def __init__(self, id, x, y, radius):
        Unit.__init__(self, id, x, y)

        self.radius = radius
