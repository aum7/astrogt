# ruff: noqa: E402
# ruff: noqa: E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.swecore import SweCore  # event data


class SwePositions:
    """get positions of planets"""

    def __init__(self, app=None):
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        # connect to data-changed signal
        self._signal._connect("event-one-changed", self.on_event_one_changed)
        self._signal._connect("event-two-changed", self.on_event_two_changed)
        # get all needed data from swe core
        self.swe_core = SweCore(self._app)
        self.event_one_data = self.swe_core.event_one_swe_ready()
        self.event_two_data = self.swe_core.event_two_swe_ready()
        self.flags = self.swe_core._get_swe_flags()
        print(f"flags : {self.flags}")

    def on_event_one_changed(self, data, *args):
        self.event_one_data = data
        # event = self.data.get("event one")
        print(f"event 1 changed : {self.event_one_data}")
        # self.swe_one_data()
        # self._notify.success(
        #     f"e1 name : {self.data.event_one_name}",
        #     source="swepositions",
        # )

    def on_event_two_changed(self, data, *args):
        self.event_two_data = data
        # event = self.data.get("event two")
        print(f"event 2 changed : {self.event_two_data}")

    def swe_one_data(self):
        print(f"swepositions : e1 : {self.event_one_data} OLO")
        # check if data in swecore is ready
        for event_name, event_data in self.event_one_data.items():
            if event_data and len(event_data) >= 4:
                jd_ut = event_data[3]
                if isinstance(jd_ut, float):  # and'jd_ut_swe' in datetime_dict:
                    print(f"e1 : {event_name} | jd : {jd_ut}")
        return self.event_one_data
