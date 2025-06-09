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
        self.guests = guests or []
        self.info_data = None
        self.radius = 0

    def add_guest(self, objects):
        self.guests.extend(objects)

    def draw(self, cr, width, height):
        """will draw small circles as objects / planets marker"""
        cx, cy = width / 2, height / 2
        base = min(width, height) * 0.5
        if self.layer == "info":
            radius = base * 0.5
            cr.arc(cx, cy, radius, 0, 2 * pi)
            cr.set_source_rgba(0.9, 0.9, 0.9, 0.8)
            cr.fill_preserve()
            cr.set_source_rgba(0.3, 0.3, 0.4, 1)
            cr.stroke()
            # if hasattr(self, "info_data"):
            if self.info_data:
                info = self.info_data
                text = f"{info.get('name', '')}\n{info.get('country', '')}\n{info.get('city', '')}\n{info.get('location', '')}\n{info.get('datetime')}"
                cr.set_source_rgba(0, 0, 0, 1)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(12)
                xbearing, ybearing, tw, th, xadvance, yadvance = cr.text_extents(text)
                cr.move_to(cx - tw / 2, cy - th / 2)
                cr.show_text(text)
            return
        # draw circle at correct radius
        self.radius = base * 0.9
        cr.arc(cx, cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.7, 0.7, 0.8, 0.4)
        cr.fill_preserve()
        cr.set_source_rgba(0.3, 0.3, 0.4, 1)
        cr.stroke()
        # draw guests
        for obj in self.guests:
            obj.draw(cr, cx, cy, self.radius)
