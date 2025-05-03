# sweph/calculations/positions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from user.settings import OBJECTS, CHART_SETTINGS


class SwePositions:
    def __init__(self, app=None):
        # print("swepositions : olo")
        self._app = app or Gtk.Application.get_default()
        # self._data = getattr(self._app, "e1_swe", {}) if app is None else {}
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        self._signal._connect("event-one-changed", self.event_one_changed)
        self._signal._connect("event-two-changed", self.event_two_changed)

    def event_one_changed(self, data):
        self._notify.debug(
            "e1 changed",
            source="positions",
            route=["terminal"],
        )
        self.positions_page("e1")

    def event_two_changed(self, data):
        self._notify.debug(
            "e2 changed",
            source="positions",
            route=["terminal"],
        )
        self.positions_page("e2")

    def calculate_positions(self, event):
        """calculate planetary positions & present in a table as stack widget"""
        # get selected objects
        if event == "e2":
            src = getattr(self._app, "e2_swe", {})
            objs = getattr(self._app, "selected_objects_e2", set())
        else:
            src = getattr(self._app, "e1_swe", {})
            objs = getattr(self._app, "selected_objects_e1", set())
        # test todo
        print(f"positions : src (swe) : {src}\n\tselobjs : {objs}")
        # swe.calc_ut() with topocentric flag needs topographic location
        if "topocentric" in self._app.selected_flags and all(
            k in src for k in ("lon", "lat", "alt")
        ):
            """coordinates are reversed here : lon lat alt"""
            print("found 'topocentric' flag")
            swe.set_topo(src["lon"], src["lat"], src["alt"] if src["alt"] else None)
        jd_ut = src.get("jd_ut")
        # print(f"jd_ut : {jd_ut}")
        if jd_ut is None:
            return []
        # print(f"objs : {objs}")
        positions_out = []
        for obj in objs:
            obj_int = self.object_name_to_int(obj)
            if obj_int is None:
                continue
            # we also need flags ; calc_ut() returns array of 6 floats + error string :
            # longitude, latitude, distance
            # lon speed, lat speed, dist speed
            value = swe.calc_ut(jd_ut, obj_int, self._app.sweph_flag)

            degree = (
                value[0][0]
                if isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[0], tuple)
                else value
            )
            positions_out.append((str(obj_int), degree))
        print(f"\n\tpositions_out : {positions_out}\n")
        return positions_out

    def table_positions(self, positions):
        """create a table of planetary positions"""
        # table = Gtk.Grid()
        table = Gtk.ListStore(str, str)
        for body, value in positions:
            table.append([body, f"{value:.6f}"])
        view = Gtk.TreeView(model=table)
        for idx, title in enumerate(("body", "value")):
            rend = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, rend, text=idx)
            view.append_column(col)
        scw_pos = Gtk.ScrolledWindow()
        scw_pos.set_child(view)
        return scw_pos

    def positions_page(self, event):
        pos = self.calculate_positions(event)
        if not pos:
            msg = "no swe e2 data" if event == "e2" else "no swe e1 data"
            return Gtk.Label(label=msg)
        return self.table_positions(pos)

    def object_name_to_int(self, name: str) -> int | None:
        # if name == "true node" and CHART_SETTINGS.get("mean node")[0]:
        if name == "true node" and CHART_SETTINGS["mean node"][0]:
            name = "mean node"
        for obj in OBJECTS.values():
            if obj[0] == name:
                return obj[3]
        if name == "mean node":
            return 10
        return None

    # def object_int_to_name(self, obj_int: int) -> str | None:
    #     # swe.get_planet_name(obj_int)
    #     for obj in OBJECTS.values():
    #         if obj[3] == obj_int:
    #             return OBJECTS.keys()
