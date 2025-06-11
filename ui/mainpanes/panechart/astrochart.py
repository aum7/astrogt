# ui/mainpanes/panechart/astrochart.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.mainpanes.panechart.chartcircles import CircleEvent, CircleSigns, CircleInfo
from math import pi, cos, sin, radians


class AstroChart(Gtk.Box):
    """main astro chart widget for circles & objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # cairo drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.append(self.drawing_area)
        # initial data
        self.positions = {}
        self.houses = {}
        self.e1_chart_info = {}
        # subscribe to signals
        signal = self.app.signal_manager
        signal._connect("event_changed", self.event_changed)
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)

    def event_changed(self, event):
        if event == "e1":
            self.e1_chart_info = self.app.e1_chart
            print(f"astrochart : e1chart : {self.e1_chart_info}")
            self.queue_draw()

    def positions_changed(self, event, positions):
        if event == "e1":
            self.positions = positions
            print(f"astrochart : positions : {self.positions}")
            self.queue_draw()

    def houses_changed(self, event, houses):
        if event == "e1":
            self.houses = houses
            print(f"astrochart : houses : {self.houses}")
            self.queue_draw()

    def e2_cleared(self, event):
        """clear event 2 circles"""
        if event == "e2":
            print(f"astrochart : {event} cleared")
            self.queue_draw()

    def draw(self, area, cr, width, height):
        # get center and base radius
        cx = width / 2
        cy = height / 2
        base = min(width, height) * 0.5
        # get chart info data
        e1_chart_info = getattr(self.app, "e1_chart", {})
        # chart circles
        circle_event = CircleEvent(
            radius=base * 0.8,
            cx=cx,
            cy=cy,
            guests=[
                self.create_astro_object(obj)
                for obj in self.positions.values()
                if isinstance(obj, dict) and "lon" in obj
            ],
            houses=self.houses if self.houses else [],
        )
        circle_signs = CircleSigns(radius=base * 0.95, cx=cx, cy=cy)
        circle_info = CircleInfo(
            radius=base * 0.5, cx=cx, cy=cy, event_data=e1_chart_info
        )
        # draw layers from bottom (event) to top (info)
        circle_event.draw(cr)
        circle_signs.draw(cr)
        circle_info.draw(cr)

    def create_astro_object(self, obj):
        return AstroObject(obj)


class AstroObject:
    def __init__(self, data):
        self.data = data

    def draw(self, cr, cx, cy, radius):
        angle = radians(self.data.get("lon", 0))
        x = cx + radius * cos(angle)
        y = cy + radius * sin(angle)
        # simple circle marker for object / planet
        cr.arc(x, y, 8, 0, 2 * pi)
        color = self.data.get("color", (0.2, 0.3, 0.8, 1))
        cr.set_source_rgba(*color)
        cr.fill()
