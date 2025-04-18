# sweph/calculations/positions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.sidepane import panelsettings


class SwePositions:
    def __init__(self, event_data=None, app=None):
        print("swepositions : olo")
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        self.event_data = event_data
        self._signal._connect("event-one-changed", self.on_event_one_changed)
        self._signal._connect("event-two-changed", self.on_event_two_changed)

    def on_event_one_changed(self, event_data):
        print(f"swepositions : event one changed : {event_data}")
        # self.positions_page()

    def on_event_two_changed(self, event_data):
        print(f"swepositions : event two changed : {event_data}")

    def calculate_positions(self):
        """calculate planetary positions & present in a table as stack widget"""
        app = Gtk.Application.get_default()
        if not app or not hasattr(app, "e1_swe"):
            return {}
        e1swe = app.e1_swe
        jd_ut = e1swe.get("jd_ut")
        if jd_ut is None:
            return {}
        # get selected objects
        selected_objs = getattr(panelsettings, "selected_objects", set())
        return swe.calc_ut(jd_ut, list(selected_objs))

    def table_positions(self, positions):
        """create a table of planetary positions"""
        table = Gtk.Grid()
        table.set_column_homogenous(True)
        row = 0
        for body, value in positions.items():
            lbl_body = Gtk.Label(label=str(body))
            lbl_val = Gtk.Label(label=str(value))
            table.attach(lbl_body, 0, row, 1, 1)
            table.attach_next_to(lbl_val, lbl_body, Gtk.PositionType.Right, 1, 1)
            row += 1
        return table

    def positions_page(self):
        pos = self.calculate_positions()
        if not pos:
            return Gtk.Label(label="no e1 swe data")
        return self.table_positions(pos)
