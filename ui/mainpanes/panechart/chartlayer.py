# ui/mainpanes/panechart/chartlayer.py
# ruff: noqa: E402
# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk  # type: ignore
from math import pi


class CircleLayer:
    """layer where circles as charts live happy & prosperous life"""

    def __init__(self, layer="info", chart=None, guests=None):
        self.layer = layer
        self.chart = chart
        # astrological objects as guests of cosmos
        self.guests = []
        self.radius = 0

    def add_guest(self, objects):
        self.guests.extend(objects)

    def draw(self, cr, width, height):
        """will draw small circles as objects / planets marker"""
        cx, cy = width / 2, height / 2
        base = min(width, height) * 0.5
        # draw circle at correct radius
        self.radius = base * (0.7 if self.layer == 0 else 0.9)
        cr.arc(cx, cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.7, 0.7, 0.8, 1.0 if self.layer == 1 else 0.4)
        cr.fill_preserve()
        cr.set_source_rgba(0.3, 0.3, 0.4, 1)
        cr.stroke()
        # draw guests
        for obj in self.guests:
            obj.draw(cr, cx, cy, self.radius)
