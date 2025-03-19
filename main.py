# ruff: noqa: E402
from ui.mainwindow import MainWindow
from ui.notifyuser import NotifyManager
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # type: ignore


class AstrogtApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="aum.astrogt.app",
        )
        self.notify_manager = NotifyManager()

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
        self.notify_manager.success("astrogt app started", source="main.py", timeout=7)
        win.present()


if __name__ == "__main__":
    app = AstrogtApp()
    app.run(None)
