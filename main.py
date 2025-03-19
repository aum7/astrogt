# ruff: noqa: E402
from ui.mainwindow import MainWindow
import gi

gi.require_version("Gtk", "4.0")
# gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # type: ignore


class AstrogtApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="aum.astrogt.app",
            # flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        # self.ovl_toast_adw = Adw.ToastOverlay()

    def do_activate(self):
        # win = MainWindow(application=self)
        win = Gtk.ApplicationWindow(application=self)
        win.connect("destroy", lambda x: self.quit())
        # self.ovl_toast_adw = Adw.ToastOverlay()
        # content would be main_window (gtk.applicationwindow)
        # box_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # box_content.append(win)
        # label = Gtk.Label(label="olo lo")
        # box_content.append(label)
        # button = Gtk.Button(label="show toast")
        # button.connect("clicked", self.on_show_toast, self.ovl_toast_adw)
        # pass directly win
        # here child would be grid
        # adwaita toast overlay
        # self.ovl_toast_adw.set_child(box_content)
        # self.ovl_toast_adw.set_transient_for(self)
        # win.set_child(self.ovl_toast_adw)
        win.present()

    # def on_show_toast(self, button, overlay):
    #     toast = Adw.Toast.new("olo toast")
    #     toast.set_timeout(3)
    #     overlay.add_toast(toast)
    # toast.show()


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
