# ui/mainpanes/panechart/astrochart.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.mainpanes.panechart.chartcircles import CircleEvent, CircleSigns, CircleInfo
from user.settings import OBJECTS
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
        self.ascmc = None
        self.e1_chart_info = {}
        self.chart_settings = getattr(self.app, "chart_settings", {})
        self.extra_data = {}
        # subscribe to signals
        signal = self.app.signal_manager
        signal._connect("event_changed", self.event_changed)
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)
        signal._connect("settings_changed", self.settings_changed)

    def event_changed(self, event):
        if event == "e1":
            self.e1_chart_info = getattr(self.app, "e1_chart", {})
            # print("astrochart : e1 changed")
        self.drawing_area.queue_draw()

    def positions_changed(self, event, positions):
        if event == "e1":
            self.positions = positions
        self.drawing_area.queue_draw()
        # print(f"astrochart : {event} positions changed")

    def houses_changed(self, event, houses):
        if event == "e1":
            try:
                cusps, ascmc = houses
            except Exception as e:
                self.notify(
                    f"invalid houses data\n\terror :\n\t{e}",
                    source="astrochart",
                    route=["terminal"],
                )
            self.houses = cusps
            self.ascmc = ascmc
        # construct extra info
        self.extra_data["hsys"] = getattr(self.app, "selected_house_sys_str")
        self.drawing_area.queue_draw()
        # print(f"astrochart : {event} houses changed")

    def e2_cleared(self, event):
        """clear event 2 circles"""
        if event == "e2":
            self.notify.info(
                f"{event} cleared",
                source="astrochart",
                route=["terminal"],
            )
        self.drawing_area.queue_draw()

    def settings_changed(self, arg):
        self.chart_settings = getattr(self.app, "chart_settings", {})
        self.drawing_area.queue_draw()

    def draw(self, area, cr, width, height):
        # get center and base radius
        cx = width / 2
        cy = height / 2
        base = min(width, height) * 0.5
        # code block : if fixed asc > rotate circles > asc at left
        if self.chart_settings.get("fixed asc", True):
            asc_angle = radians(self.ascmc[0]) if self.ascmc else 0
            cr.save()
            cr.translate(cx, cy)
            cr.rotate(asc_angle)
            cr.translate(-cx, -cy)
        # sort by scale : smaller in front of larger circles
        guests = sorted(
            [
                self.create_astro_object(obj)
                for obj in self.positions.values()
                if isinstance(obj, dict) and "lon" in obj
            ],
            key=lambda o: o.scale,
            reverse=True,
        )
        # construct extra info
        self.extra_data["zod"] = "sid" if self.app.is_sidereal else "tro"
        self.extra_data["aynm"] = (
            self.app.selected_ayan_str if self.app.selected_ayan_str else "-"
        )
        # chart circles
        circle_event = CircleEvent(
            radius=base * 0.8,
            cx=cx,
            cy=cy,
            guests=guests,
            houses=self.houses if self.houses else [],
            ascmc=self.ascmc if self.ascmc else [],
            chart_settings=self.chart_settings,
        )
        circle_signs = CircleSigns(radius=base * 0.95, cx=cx, cy=cy)
        circle_info = CircleInfo(
            self.notify,
            radius=base * 0.5,
            cx=cx,
            cy=cy,
            chart_settings=self.chart_settings,
            event_data=self.e1_chart_info,
            extra_info=self.extra_data,
        )
        # draw layers from bottom (signs) to top (info)
        circle_signs.draw(cr)
        circle_event.draw(cr)
        # restore context if chart rotation was applied
        if self.chart_settings.get("fixed asc", False):
            cr.restore()
        # code block end
        # draw info circle last > no text rotation
        circle_info.draw(cr)

    def create_astro_object(self, obj):
        return AstroObject(obj)


class AstroObject:
    def __init__(self, data):
        self.data = data
        # print(f"astrochart : objects : {data}")
        self.size = 8
        name = self.data.get("name", "su").lower()
        # default color & scale
        self.color = (0.1, 0.1, 0.1, 0.5)
        self.scale = 1.0

        for obj in OBJECTS.values():
            if obj[0].lower() == name:
                self.color = obj[4]
                self.scale = obj[5]
                break

    def draw(self, cr, cx, cy, radius):
        # compute angle & draw in ccw direction, start at left (ari)
        angle = pi - radians(self.data.get("lon", 0))
        # determine radius by scale
        obj_size = self.size * self.scale
        x = cx + radius * cos(angle)
        y = cy + radius * sin(angle)
        # simple circle marker for object / planet
        cr.arc(x, y, obj_size, 0, 2 * pi)
        cr.set_source_rgba(*self.color)
        cr.fill()
