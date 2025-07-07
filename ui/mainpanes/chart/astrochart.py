# ui/mainpanes/panechart/astrochart.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.mainpanes.chart.rings import (
    Info,
    Event,
    Signs,
    Naksatras,
    Harmonic,
    P1Progress,
    P3Progress,
    SolarReturn,
    LunarReturn,
    Transits,
)
from user.settings import OBJECTS
from math import pi, cos, sin, radians


class AstroChart(Gtk.Box):
    """main astro chart widget for rings & objects"""

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
        self.extra_info = {}
        self.stars = {}
        # subscribe to signals
        signal = self.app.signal_manager
        signal._connect("event_changed", self.event_changed)
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)
        signal._connect("settings_changed", self.settings_changed)
        signal._connect("stars_changed", self.stars_changed)
        signal._connect("p1_changed", self.p1_changed)

    def event_changed(self, event):
        # main data - event - changed
        if event == "e1":
            self.e1_chart_info = getattr(self.app, "e1_chart", {})
            # print("astrochart : e1 changed")
        self.drawing_area.queue_draw()

    def positions_changed(self, event):
        if event == "e1":
            self.positions = (
                self.app.e1_positions if hasattr(self.app, "e1_positions") else None
            )
            # self.positions = positions
        self.drawing_area.queue_draw()
        # print(f"astrochart : {event} positions changed")

    def houses_changed(self, event):
        if event == "e1":
            try:
                houses = getattr(self.app, "e1_houses", None)
                if houses:
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
        self.extra_info["hsys"] = getattr(self.app, "selected_house_sys_str")
        self.drawing_area.queue_draw()
        # print(f"astrochart : {event} houses changed")

    def e2_cleared(self, event):
        # clenup after event 2 deletion
        """clear event 2 rings"""
        if event == "e2":
            self.notify.info(
                f"{event} cleared",
                source="astrochart",
                route=["terminal"],
            )
        self.drawing_area.queue_draw()

    def settings_changed(self, arg):
        # grab data & redraw
        self.chart_settings = getattr(self.app, "chart_settings", {})
        self.drawing_area.queue_draw()

    def stars_changed(self, event, stars):
        self.stars = stars
        for name, (lon, nomenclature) in stars.items():
            name = name
            lon = lon
            nomenclature = nomenclature
            # print(f"name : {name} | lon : {lon} | designation : {nomenclature}")
        self.drawing_area.queue_draw()

    def p1_changed(self, event):
        # progressions changed
        if event == "e2":
            self.p1_pos = getattr(self.app, "p1_positions", {})
            self.p1_arcs = getattr(self.app, "p1_directions", {})
        self.drawing_area.queue_draw()

    def draw(self, area, cr, width, height):
        # get center and base radius
        msg = ""
        cx = width / 2
        cy = height / 2
        # size of application pane(s)
        base = min(width, height) * 0.5
        font_scale = base / 300.0
        # sort by scale : smaller in front of larger rings
        guests = {}
        if self.positions and isinstance(self.positions, dict):
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
        self.extra_info["zod"] = "sid" if self.app.is_sidereal else "tro"
        self.extra_info["aynm"] = (
            self.app.selected_ayan_str if self.app.selected_ayan_str else "-"
        )
        # draw rings
        max_radius = base * 0.97
        # outer rings linked to event 2 :
        # - primary & tertiary progression
        # - solar & lunar return
        # - transits
        # includes naksatras & harmonic ring
        outer_rings = []
        if getattr(self.app, "e2_active", False):
            msg += "e2 is active\n"
            # collect outer ring candidates
            if self.chart_settings.get("transits"):
                outer_rings.append("transits")
            if self.chart_settings.get("solar return"):
                outer_rings.append("solar return")
            if self.chart_settings.get("lunar return"):
                outer_rings.append("lunar return")
            if self.chart_settings.get("p1 progress"):
                outer_rings.append("p1 progress")
            if self.chart_settings.get("p3 progress"):
                outer_rings.append("p3 progress")
        if self.chart_settings.get("harmonic ring", "").strip():  # is not None:
            outer_rings.append("harmonic")
        if self.chart_settings.get("naksatras ring", ""):
            outer_rings.append("naksatras")
        msg += f"outerrings : {outer_rings}\n"
        # reduce mandatory e1 factor per ring : e2 first
        outer_portion = {
            "transits": 0.07,
            "lunar return": 0.07,
            "solar return": 0.07,
            "p3 progress": 0.07,
            "p1 progress": 0.07,
            "harmonic": 0.06,
            "naksatras": 0.06,
        }
        radius_outer = {}
        cumulative = 0.0
        # use fixed order for event 2 rings
        for ring, portion in outer_portion.items():
            if ring in outer_rings:
                radius_outer[ring] = max_radius * (1 - cumulative)
                cumulative += portion
        radius_inner = 1 - cumulative
        # --- rotate block : if fixed asc > rotate rings
        if self.chart_settings.get("fixed asc", False) and self.ascmc:
            asc_angle = radians(self.ascmc[0])
            cr.save()
            cr.translate(cx, cy)
            cr.rotate(asc_angle)
            cr.translate(-cx, -cy)
        # --- outer rings : transits
        if "transits" in outer_rings:
            ring_transits = Transits(
                radius=radius_outer.get("transits", max_radius),
                cx=cx,
                cy=cy,
                font_size=int(12 * font_scale),
                chart_settings=self.chart_settings,
            )
            ring_transits.draw(cr)
        # --- lunar return
        if "lunar return" in outer_rings:
            ring_lunar = LunarReturn(
                radius=radius_outer.get("lunar return", max_radius),
                cx=cx,
                cy=cy,
                font_size=int(12 * font_scale),
                chart_settings=self.chart_settings,
            )
            ring_lunar.draw(cr)
        # --- solar return
        if "solar return" in outer_rings:
            ring_solar = SolarReturn(
                radius=radius_outer.get("solar return", max_radius),
                cx=cx,
                cy=cy,
                font_size=int(12 * font_scale),
                chart_settings=self.chart_settings,
            )
            ring_solar.draw(cr)
        # --- tertiary progressions
        if "p3 progress" in outer_rings:
            ring_p3 = P3Progress(
                radius=radius_outer.get("p3 progress", max_radius),
                cx=cx,
                cy=cy,
                font_size=int(12 * font_scale),
                chart_settings=self.chart_settings,
            )
            ring_p3.draw(cr)
        # --- primary progressions
        if "p1 progress" in outer_rings:
            ring_p1 = P1Progress(
                radius=radius_outer.get("p1 progress", max_radius),
                cx=cx,
                cy=cy,
                font_size=int(12 * font_scale),
                chart_settings=self.chart_settings,
            )
            ring_p1.draw(cr)
        # --- optional rings : harmonic
        if "harmonic" in outer_rings:
            # msg += f"harmonic ring : {self.chart_settings.get('harmonic ring', '').strip()}\n"
            try:
                division_value = int(
                    self.chart_settings.get("harmonic ring", "").strip()
                )
                if division_value not in {1, 7, 9, 11}:
                    division = None
                else:
                    division = division_value
            except Exception:
                division = None
            if division:
                ring_harmonic = Harmonic(
                    self.notify,
                    radius=radius_outer.get("harmonic", max_radius),
                    cx=cx,
                    cy=cy,
                    # division=1,
                    division=division,
                    font_size=int(12 * font_scale),
                )
                ring_harmonic.draw(cr)
        # --- naksatras
        if "naksatras" in outer_rings:
            naks_num = 28 if self.chart_settings.get("28 naksatras", False) else 27
            first_nak = int(self.chart_settings.get("1st naksatra", 1))
            ring_naksatras = Naksatras(
                radius=radius_outer.get("naksatras", ""),
                cx=cx,
                cy=cy,
                font_size=int(14 * font_scale),
                naks_num=naks_num,
                first_nak=first_nak,
            )
            ring_naksatras.draw(cr)
        # --- outer rings end
        # --- mandatory inner rings
        # chart rings
        ring_signs = Signs(
            radius=max_radius * radius_inner,
            cx=cx,
            cy=cy,
            font_size=int(17 * font_scale),
            stars=self.stars,
        )
        ring_signs.draw(cr)
        ring_event = Event(
            radius=max_radius * radius_inner * 0.92,
            cx=cx,
            cy=cy,
            font_size=int(18 * font_scale),
            guests=guests,
            houses=self.houses if self.houses else [],
            ascmc=self.ascmc if self.ascmc else [],
            chart_settings=self.chart_settings,
        )
        ring_event.draw(cr)
        # restore context if chart rotation was applied
        if self.chart_settings.get("fixed asc", False) and self.ascmc:
            cr.restore()
        # --- rotate block end
        # draw info ring last > no text rotation
        ring_info = Info(
            self.notify,
            radius=max_radius * radius_inner * 0.4,
            cx=cx,
            cy=cy,
            font_size=int(16 * font_scale),
            chart_settings=self.chart_settings,
            event_data=self.e1_chart_info,
            extra_info=self.extra_info,
        )
        ring_info.draw(cr)
        self.notify.debug(
            msg,
            source="astrochart",
            route=["terminal"],
        )

    def create_astro_object(self, obj):
        return AstroObject(obj)


class AstroObject:
    def __init__(self, data):
        self.data = data
        # print(f"astrochart : objects : {data}")
        self.size = 0.7
        name = self.data.get("name", "su").lower()
        # default color & scale
        self.color = (0.1, 0.1, 0.1, 0.5)
        self.scale = 1.0

        for obj in OBJECTS.values():
            if obj[0].lower() == name:
                self.color = obj[4]
                self.scale = obj[5]
                break

    def draw(self, cr, cx, cy, radius, obj_scale=1.0):
        # compute angle & draw in ccw direction, start at left (ari)
        angle = pi - radians(self.data.get("lon", 0))
        # determine radius by scale
        # obj_size = self.scale * obj_scale
        obj_size = self.size * self.scale * obj_scale
        x = cx + radius * cos(angle)
        y = cy + radius * sin(angle)
        # simple ring marker for object / planet
        cr.arc(x, y, obj_size, 0, 2 * pi)
        cr.set_source_rgba(*self.color)
        cr.fill()
