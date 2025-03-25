# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Any, Optional
from .handlers import ContextManager
from .sidepane.sidepane import SidePaneManager
from .uisetup import UISetup
from .hotkeymanager import HotkeyManager


class MainWindow(
    Gtk.ApplicationWindow,
    SidePaneManager,
    ContextManager,
    UISetup,
):
    """main application window, combining ui, handlers & panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window"""
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        SidePaneManager.__init__(self, app=self.get_application())
        self._app = self.get_application() or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self.swe_core = self._app.swe_core
        self.set_title("astrogt")
        self.set_default_size(800, 600)
        # setup ui : side pane
        self.setup_revealer()
        self.setup_css()
        # 4 resizable panes for charts & tables etc
        self.setup_main_panes()
        self.setup_context_controllers()
        # hotkey manager
        self._hotkeys = HotkeyManager(self)
        self.setup_hotkeys()
        # intercept toggle pane button
        self._hotkeys.intercept_button_controller(self.btn_toggle_pane, "toggle_pane")

    def on_toggle_pane(self, button: Optional[Gtk.Button] = None) -> None:
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)

    def setup_hotkeys(self):
        # register additional hotkeys
        self._hotkeys.register_hotkey("h", self.show_help)
        self._hotkeys.register_hotkey("s", self.on_toggle_pane)
        self._hotkeys.register_hotkey("c", self.center_all_panes)
        self._hotkeys.register_hotkey("Up", self.obc_arrow_up)
        self._hotkeys.register_hotkey("Down", self.obc_arrow_dn)
        self._hotkeys.register_hotkey("Left", self.obc_arrow_l)
        self._hotkeys.register_hotkey("Right", self.obc_arrow_r)
        self._hotkeys.register_hotkey("n", self.obc_time_now)
        self._hotkeys.register_hotkey("e", self.event_toggle_selected)

    def get_focused_event_data(self, event_name: str, widget=None) -> None:
        """get data for focused event on datetime entry"""
        # print("get_focused_event_data called")
        if event_name == "event one":
            event_one_data = self.EVENT_ONE.get_event_data() if self.EVENT_ONE else None
            self.swe_core.get_event_one_data(event_one_data)
        elif event_name == "event two":
            event_two_data = self.EVENT_TWO.get_event_data() if self.EVENT_TWO else None
            self.swe_core.get_event_two_data(event_two_data)

    # hotkey action functions
    def show_help(self):
        self._notify.debug(
            "manual\n"
            "\nhover mouse over buttons & text = show tooltips"
            "\nhover mouse over notification message = persist message"
            "\nesc : discard message\n\nhotkeys (hk)"
            "\nh : show help (this message)"
            "\ns : toggle side pane"
            "\nc : center main panes"
            "\ne : toggle selected event for time change"
            "\narrow keys : up/down = change period | left/right = change time"
            "\n\tfor selected event"
            "\nn : set time now (utc) for selected event"
            "\n\ttime now is set for event location, not your computer local time"
            "\ntab/shift+tab : navigate between widgets in side pane"
            "\nspace/enter : activate button / dropdown when focused"
            "\n\nnote : if entry (text) field is focused, hotkeys will not work"
            "\n\t(text field will 'consume' key press)",
            source="help",
            timeout=5,
            route=["user"],
        )

    # hotkey actions end
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
