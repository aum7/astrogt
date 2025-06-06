# ui/mainpanes/panechart/astrochart.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.mainpanes.panechart.chartlayer import CircleLayer
from ui.mainpanes.panechart.astroobjects import AstroObject


class AstroChart(Gtk.Box):
    """main astro chart widget for circles & objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app = Gtk.Application.get_default()
        notify = app.notify_manager
        notify.debug(
            "astrochart : OLO",
            source="astrochart",
            route=["terminal"],
        )
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.append(self.drawing_area)
        # self.set_child(self.drawing_area)
        # chart circles
        self.circles = {
            # top layer
            "info": CircleLayer(layer="info", chart=self, guests=[]),
            # mandatory event 1 layer
            "event": CircleLayer(layer="event", chart=self, guests=[]),
            # optional layers : transit
            # "transit": CircleLayer(layer="info", chart=self, guests=[]),
            # progression
            # "progression": CircleLayer(layer="progression", chart=self, guests=[]),
            # solar return
            # "solar return": CircleLayer(layer="solar return", chart=self, guests=[]),
        }
        # positions & houses needed
        self.positions = {}
        self.houses = []
        # list of objects
        # self.obj_e1 = app.selected_objects_e1
        # assign objects to circles
        # self.circles["event"].add_guest(self.astro_objects)
        # drawing area setup

    def update_data(self, positions, houses):
        self.positions = positions
        self.houses = houses
        self.circles["event"].guests = [
            AstroObject(obj)
            for obj in positions.values()
            if isinstance(obj, dict) and "lon" in obj
        ]
        self.queue_draw()

    def draw(self, area, cr, width, height):
        for circle in self.circles.values():
            circle.draw(cr, width, height)
