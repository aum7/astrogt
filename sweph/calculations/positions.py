# ruff: noqa: E402
# ruff: noqa: E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
# from sweph.swecore import SweCore  # event data


class SwePositions:
    """get positions of planets"""

    def __init__(self, app=None):
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        # connect to data-changed signal
        self._signal._connect("event-one-changed", self.on_event_one_changed)
        self._signal._connect("event-two-changed", self.on_event_two_changed)
        self.swe_core = self._app.swe_core
        self.e1data = self.swe_core.event_one_swe_ready()
        self.e2data = self.swe_core.event_two_swe_ready()

    def on_event_one_changed(self, data, *args):
        self.e1data = data
        # event = self.data.get("event one")
        print(f"event 1 changed : {self.e1data}")
        # self.swe_one_data()
        # self._notify.success(
        #     f"e1 name : {self.data.event_one_name}",
        #     source="swepositions",
        # )

    def on_event_two_changed(self, data, *args):
        self.e2data = data
        print(f"event 2 changed : {self.e2data}")
        # process data
        for event_name, event_data in self.e2data.items():
            if event_data and len(event_data) >= 4:
                jd_ut = event_data[3]
                if isinstance(jd_ut, float):  # and'jd_ut_swe' in datetime_dict:
                    print(f"e2 : {event_name} | jd_ut : {jd_ut}")
        return self.e1data
