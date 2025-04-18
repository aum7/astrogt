# sweph/calculations/positions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SwePositions:
    def __init__(self, app=None):
        # print("swepositions : olo")
        self._app = app or Gtk.Application.get_default()
        self._data = getattr(self._app, "e1_swe", {}) if app is None else {}
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        self._signal._connect("event-one-changed", self.on_event_one_changed)
        self._signal._connect("event-two-changed", self.on_event_two_changed)
        self._signal._connect("event-two-erased", self.on_event_two_erased)

    def on_event_one_changed(self, event_data):
        self._notify.debug(
            f"e1 changed : {event_data}",
            source="positions",
            route=["terminal"],
        )
        self.positions_page()

    def on_event_two_changed(self, event_data):
        self._notify.debug(
            f"e2 changed : {event_data}",
            source="positions",
            route=["terminal"],
        )

    def on_event_two_erased(self, event_data):
        self._notify.debug(
            f"e2 erased : {event_data}",
            source="positions",
            route=["terminal"],
        )

    def calculate_positions(self):
        """calculate planetary positions & present in a table as stack widget"""
        src = self._data or getattr(self._app, "e1_swe", {})
        jd_ut = src.get("jd_ut")
        print(f"jd_ut : {jd_ut}")
        if jd_ut is None:
            print("jd_ut none")
            return []
        # get selected objects
        objs = getattr(self._app, "selected_objects", set())
        print(f"objs : {objs}")
        positions_out = []
        for body in objs:
            positions_out.append((body, swe.calc_ut(jd_ut, body)))
        print(f"positions_out : {positions_out}")
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
            print(f"col : {col}")
            view.append_column(col)
        scw_pos = Gtk.ScrolledWindow()
        scw_pos.set_child(view)
        return scw_pos

    def positions_page(self):
        pos = self.calculate_positions()
        if not pos:
            return Gtk.Label(label="no e1 swe data")
        return self.table_positions(pos)
