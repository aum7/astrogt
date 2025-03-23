# ruff: noqa: E402
# ruff: noqa: E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.swecore import SweCore  # event data
# from ui.notifymanager import NotifyManager
# from ui.signalmanager import SignalManager


class SwePositions:
    """get positions of planets"""

    def __init__(self, get_application=None):
        # print("swepositions : initialising swepositions ...")
        self._get_application = get_application or Gtk.Application.get_default()
        self.notify_manager = self._get_application.notify_manager
        # self.notify_manager = NotifyManager(self._get_application)
        self.signal_manager = self._get_application.signal_manager
        # self.signal_manager = SignalManager(self._get_application)
        # subscribe to data-changed signal
        # use single swecore instance for state & signaling
        self.signal_manager._connect("event-one-changed", self.on_event_one_changed)
        self.signal_manager._connect("event-two-changed", self.on_event_two_changed)
        self.swe_core = SweCore(self._get_application)
        self.data = self.swe_core.swe_ready_data()
        # self.swe_data()

    def on_event_one_changed(self, data, *args):
        print("positions : oneventonechanged called")
        self.data = data
        # event = self.data.get("event one")
        print(f"event 1 changed : {self.data}")
        # self.swe_data()
        # self.notify_user(
        #     f"e1 name : {self.data.event_one_name}",
        #     source="swepositions",
        #     level="success",
        # )

    def on_event_two_changed(self, data, *args):
        print("positions : oneventtwochanged called")
        self.data = data
        # event = self.data.get("event two")
        print(f"event 2 changed : {self.data}")

    def swe_data(self):
        print(f"swepositions : {self.data} OLO")
        # check if data in swecore is ready
        for event_name, event_data in self.data.items():
            if event_data and len(event_data) >= 4:
                jd_ut = event_data[3]
                if isinstance(jd_ut, float):  # and'jd_ut_swe' in datetime_dict:
                    print(f"e : {event_name} | jd : {jd_ut}")
        return self.data

    def notify_user(self, message, **kwargs):
        app = (
            self._get_application
            # self.get_application()
            if self._get_application
            else Gtk.Application.get_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"positions :\n\t{message}")
