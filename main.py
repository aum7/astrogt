# ruff: noqa: E402
from ui.mainwindow import MainWindow
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def main():
    app = Gtk.Application(application_id="aum.astrogt.app")
    app.connect("activate", on_activate)
    app.run(None)


def on_activate(app):
    win = MainWindow(application=app)
    win.connect("destroy", lambda x: app.quit())
    win.present()


if __name__ == "__main__":
    main()
    # import sys
