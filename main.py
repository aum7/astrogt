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
            # flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.notify_manager = NotifyManager()

    def do_activate(self):
        # win = Gtk.ApplicationWindow(application=self)
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
        # self.notify_manager.setup_overlay(win)
        # test notification
        # self.notify_manager.notify("olo toast")
        win.present()


if __name__ == "__main__":
    app = AstrogtApp()
    app.run(None)

    # main()
# def main():
#     app = Gtk.Application(application_id="aum.astrogt.app")
#     app.connect("activate", on_activate)
#     app.run(None)


# def on_activate(app):
#     win = MainWindow(application=app)
#     win.connect("destroy", lambda x: app.quit())
#     win.present()
