# ruff: noqa: E402
from swe.swecore import SweCore
from ui.notifymanager import NotifyManager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SwePositions:
    def __init__(self, get_application=None):
        self.get_application = get_application
        self.swe_core = SweCore()
        self.notify_manager = NotifyManager()

        self.notify_user(
            "sweposition : {self.swe_core.event_one_name}",
            source="swepositions",
            level="debug",
        )

    def notify_user(self, message, **kwargs):
        app = (
            self.get_application()
            if self.get_application
            else Gtk.get_application_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"eventdata : {message}")
