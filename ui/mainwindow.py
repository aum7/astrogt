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
        self.hotkey_manager.register_hotkey("h", self.show_help)
        self.hotkey_manager.register_hotkey("e", self.on_toggle_pane)
        self.hotkey_manager.register_hotkey("c", self.center_all_panes)
        self.hotkey_manager.register_hotkey("Up", self.obc_arrow_up)
        self.hotkey_manager.register_hotkey("Down", self.obc_arrow_dn)
        self.hotkey_manager.register_hotkey("Left", self.obc_arrow_l)
        self.hotkey_manager.register_hotkey("Right", self.obc_arrow_r)
        self.hotkey_manager.register_hotkey("n", self.obc_time_now)

    # hotkey action functions
    def show_help(self):
        # todo
        self.show_notification(
            "manual\n"
            "\nhover mouse over buttons & text - show tooltips"
            "\nhover mouse over notification message - persist message"
            "\nesc : discard message\n\nhotkeys"
            "\nh : show help (this message)"
            "\ne : toggle side pane"
            "\nc : center all panes"
            "\narrow keys : up/down = change period | left/right = change time"
            "\n\tfor selected event"
            "\nn : set time to now for selected event"
            "\ntab/shift+tab : navigate between widgets in side pane"
            "\nspace/enter : activate button if focused",
            source="help",
            timeout=5,
        )

    # hotkey actions end
    def show_notification(self, message, source=None, timeout=3):
        """helper method to access notifictions from app instance"""
        app = self.get_application()
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, source=source, timeout=timeout)

    def center_all_panes(self) -> None:
        """center all 4 main panes"""
        if (
            hasattr(self, "pnd_main_v")
            and hasattr(self, "pnd_top_h")
            and hasattr(self, "pnd_btm_h")
        ):
            self.pnd_main_v.set_position(self.pnd_main_v.get_allocated_height() // 2)
            self.pnd_top_h.set_position(self.pnd_top_h.get_allocated_width() // 2)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_allocated_width() // 2)
