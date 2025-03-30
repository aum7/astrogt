# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # type: ignore
from ui.mainwindow import MainWindow
from ui.notifymanager import NotifyManager
from ui.signalmanager import SignalManager
from ui.timemanager import TimeManager
from sweph.swecore import SweCore
from sweph.calculations.positions import SwePositions


class AstrogtApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="aum.astrogt.app",
        )
        # global APP
        # APP = self
        # initialize attributes first
        self.selected_event = "event one"
        self.EVENT_ONE = None
        self.EVENT_TWO = None
        # global value for selected change time
        self.CHANGE_TIME_SELECTED = 0
        # time periods in seconds, used for time change todo years give weird results
        self.CHANGE_TIME_PERIODS = {
            "period_315360000": "10 years",
            "period_31536000": "1 year",
            "period_7776000": "3 months (90 d)",
            "period_2592000": "1 month (30 d)",
            "period_2360592": "1 month (27.3 d)",
            "period_604800": "1 week",
            "period_86400": "1 day",
            "period_21600": "6 hours",
            "period_3600": "1 hour",
            "period_600": "10 minutes",
            "period_60": "1 minute",
            "period_10": "10 seconds",
            "period_1": "1 second",
        }
        # managers
        self.signal_manager = SignalManager(self)
        self.notify_manager = NotifyManager(self)
        self.time_manager = TimeManager(self)
        # todo do we need this here ?
        self.swe_core = SweCore(self)
        self.swe_positions = SwePositions(self)
        self.swe_positions.swe_core = self.swe_core

    def do_activate(self):
        win = MainWindow(application=self)
        win.connect("destroy", lambda x: self.quit())
        # get existing content
        content = win.get_child()
        # create toast overlay
        toast_overlay = Adw.ToastOverlay()
        if content:
            win.set_child(None)
            toast_overlay.set_child(content)
        # set toast overlay as winddow chile
        win.set_child(toast_overlay)
        self.notify_manager.toast_overlay = toast_overlay
        # notification : code specific to this file
        self.notify_manager.notify("astrogt app started", source="main", timeout=2)
        win.present()


if __name__ == "__main__":
    app = AstrogtApp()
    app.run(None)
