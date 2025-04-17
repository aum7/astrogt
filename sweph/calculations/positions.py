# sweph/calculations/positions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.sidepane import panelsettings


class SwePositionsManager:
    def __init__(self, event_data, ui):
        self.event_data = event_data
        self.ui = ui
        self.event_data.connect("event-data-changed", self.on_event_data_changed)

    def calculate_positions(self):
        """calculate planetary positions & present in a table as stack widget"""
        app = Gtk.Application.get_default()
        if not app or not hasattr(app, "e1_swe"):
            return {}
        e1swe = app.e1_swe
        jd_ut = e1swe.get("jd_ut")
        jd_ut_ = e1swe["jd_ut"]
        if jd_ut_:
            print(f"swepositions : got jdut : {jd_ut_}")
        if jd_ut is None:
            return {}
        # get selected objects
        selected_objs = getattr(panelsettings, "selected_objects", set())
        return swe.calc_ut(jd_ut, list(selected_objs))

    def on_event_data_changed(self, emitter, data):
        print(f"swepositions : event data changed : {data}")
        pos = self.calculate_positions()
        # rebuild positions table
        page = (
            self.table_positions(pos)
            if pos
            else Gtk.Label(
                label="no data",
            )
        )
        self.ui.stack.set_page(page)

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


# class SwePositions:
#     """get positions of planets"""

#     def __init__(self, app=None):
#         self._app = app or Gtk.Application.get_default()
#         self._notify = self._app.notify_manager
#         self._signal = self._app.signal_manager
#         # connect to data-changed signal
#         self._signal._connect("event-one-changed", self.on_event_one_changed)
#         self._signal._connect("event-two-changed", self.on_event_two_changed)
#         self.swe_core = self._app.swe_core
#         self.e1data = self.swe_core.event_one_swe_ready()
#         self.e2data = self.swe_core.event_two_swe_ready()
#         # todo this is in user/settings/setupsettings.py
#         self.flags = SetupSettings()._get_swe_flags()
#         # print(f"flags : {self.flags}")

#     def on_event_one_changed(self, data, *args):
#         self.e1data = data
#         self._notify.info(
#             f"event 1 changed\n\t{self.e1data}",
#             source="swepositions",
#             route=["terminal"],
#         )

#     def on_event_two_changed(self, data, *args):
#         self.e2data = data
#         self._notify.info(
#             f"event 2 changed\n\t{self.e2data}",
#             source="swepositions",
#             route=["terminal"],
#         )
