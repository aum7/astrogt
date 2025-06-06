# ui/mainpanes/panechart/astroobject.py
from math import pi, sin, cos, radians


class AstroObject:
    def __init__(self, data):
        self.data = data

    def draw(self, cr, cx, cy, radius):
        angle = radians(self.data.get("lon", 0))
        r = radius
        x = cx + r * cos(angle)
        y = cy + r * sin(angle)
        cr.arc(x, y, 8, 0, 2 * pi)
        cr.set_source_rgba(*self.data.get("color", (0.2, 0.3, 0.8, 1)))
        cr.fill()
