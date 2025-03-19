# ruff: noqa: E402
from typing import Any
from .handlers import WindowHandlers
from .sidepane import SidePaneManager
from .uisetup import UISetup
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class MainWindow(
    Gtk.ApplicationWindow,
    WindowHandlers,
    SidePaneManager,
    UISetup,
):
    """main application window, combining ui, handlers & panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window"""
        super().__init__(*args, **kwargs)
        self.set_title("astrogt")
        self.set_default_size(800, 600)
        # setup ui
        self.setup_revealer()
        self.setup_window()
        self.setup_css()
        self.setup_main_panes()
        self.setup_context_controllers()

    def show_notification(self, message, timeout=3):
        """helper method to access notifictions from app instance"""
        app = self.get_application()
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message, timeout)
