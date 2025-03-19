# ruff: noqa: E402
from typing import Any
from .handlers import WindowHandlers
from .sidepane import SidePaneManager
from .uisetup import UISetup
from .notifyuser import NotifyManager
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw  # type: ignore


class MainWindow(
    Gtk.ApplicationWindow,
    WindowHandlers,
    SidePaneManager,
    UISetup,
    NotifyManager,
):
    """main application window, combining ui, handlers & panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window"""
        super().__init__(*args, **kwargs)
        # notifications manager
        self.setup_overlay(self)
        # self.notify_manager = NotifyManager()
        # adwaita toast overlay
        # self.ovl_toast_adw = Adw.ToastOverlay()
        # content would be main_window (gtk.applicationwindow)
        # box_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # pass directly win
        # here child would be grid
        # self.ovl_toast_adw.set_child(win)
        # self.ovl_toast_adw.set_transient_for(self)
        # self.set_child(self.ovl_toast_adw)
        # setup ui
        self.setup_revealer()
        self.setup_window()
        self.setup_css()
        self.setup_main_panes()
        self.setup_context_controllers()
