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
        self.get_application = get_application
        self.swe_core = SweCore()
        self.notify_manager = NotifyManager()

        self.notify_user(
            f"sweposition : {self.swe_core.event_one_name}",
            source="swepositions",
            level="debug",
        )

    def notify_user(self, message, **kwargs):
        app = (
            self.get_application()
            if self.get_application
            else Gtk.Application.get_default()
            # else Gtk.get_application_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"eventdata : {message}")
