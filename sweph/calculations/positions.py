# ruff: noqa: E402
# ruff: noqa: E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.swecore import SweCore  # event data
from ui.notifymanager import NotifyManager


class SwePositions:
    """get positions of planets"""

    def __init__(self, get_application=None):
        print("swepositions : initialising swepositions ...")
        self.get_application = get_application or Gtk.Application.get_default()
        # self.swe_core = SweCore()
        self.notify_manager = NotifyManager()
        self.data = SweCore.swe_ready_data()
        # subscribe to data-changed signal
        _data_changed = SweCore(Gtk.Application.get_default())
        _data_changed.connect("data-changed", self.on_data_changed)

        self.swe_data()

    def on_data_changed(self, sender):
        self.data = SweCore.swe_ready_data()
        self.swe_data()
        # self.swe_data()
        # self.notify_user(
        #     f"e1 name : {self.data.event_one_name}",
        #     source="swepositions",
        #     level="success",
        # )

    def swe_data(self):
        print(f"swereadydata : {self.data} OLO")
        # check if data in swecore is ready
        for event_name, event_data in self.data.items():
            if event_data and len(event_data) >= 4:
                jd_ut = event_data[3]
                if isinstance(jd_ut, float):  # and'jd_ut_swe' in datetime_dict:
                    print(f"e : {event_name} | jd : {jd_ut}")
        return self.data

    def notify_user(self, message, **kwargs):
        app = (
            self.get_application()
            if self.get_application
            else Gtk.Application.get_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"eventdata : {message}")
