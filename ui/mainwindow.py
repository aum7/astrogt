# ruff: noqa: E402
from typing import Any
from .handlers import WindowHandlers
from .sidepane import SidePaneManager
from .uisetup import UISetup
from .hotkeymanager import HotkeyManager
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
        # hotkey manager
        self.hotkey_manager = HotkeyManager(self)
        self.setup_hotkeys()
        # intercept toggle pane button
        self.hotkey_manager.intercept_button_controller(
            self.btn_toggle_pane, "toggle_pane"
        )

    def setup_hotkeys(self):
        # register additional hotkeys
        self.hotkey_manager.register_hotkey("h", self.toggle_help)
        self.hotkey_manager.register_hotkey("e", self.on_toggle_pane)

    # hotkey action functions
    def toggle_help(self):
        # todo
        self.show_notification("help shown")

    # hotkey actions end
    def show_notification(self, message, timeout=3):
        """helper method to access notifictions from app instance"""
        app = self.get_application()
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message, timeout)
