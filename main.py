# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # type: ignore
from ui.mainwindow import MainWindow
from ui.notifymanager import NotifyManager
from ui.signalmanager import SignalManager


class AstrogtApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="aum.astrogt.app",
        )
        # initialize attributes first
        self.selected_event = "event one"
        self.EVENT_ONE = None
        self.EVENT_TWO = None
        # managers
        self.signal_manager = SignalManager(self)
        self.notify_manager = NotifyManager(self)

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
        self.notify_manager.notify(
            "astrogt app started - press 'h' for help", source="main", timeout=3
        )
        win.present()


if __name__ == "__main__":
    app = AstrogtApp()
    app.run(None)
