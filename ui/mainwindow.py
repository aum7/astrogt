# mainwindow.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Any, Optional
from .contextmanager import ContextManager
from .sidepane.sidepane import SidepaneManager
from .uisetup import UISetup
from .hotkeymanager import HotkeyManager
from ui.helpers import _event_selection
from ui.mainpanes.panemanager import PaneManager
from sweph.calculations.positions import SwePositions


class MainWindow(
    Gtk.ApplicationWindow,
    SidepaneManager,
    PaneManager,
    ContextManager,
    UISetup,
):
    """main application window, combining ui : sidepane & main panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window"""
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        SidepaneManager.__init__(self, app=self.get_application())
        PaneManager.__init__(self)
        self._app = self.get_application() or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._swe_positions = SwePositions(app=self._app)
        self.set_title("astrogt")
        self.set_default_size(800, 600)
        # setup ui : side pane
        self.setup_revealer()
        self.setup_css()
        # 4 resizable panes for charts & tables etc
        self.setup_main_panes()
        # initialize context controllers
        self.setup_context_controllers()
        # hotkey manager
        self._hotkeys = HotkeyManager(self)
        self.setup_hotkeys()
        # intercept toggle pane button
        self._hotkeys.intercept_button_controller(self.btn_toggle_pane, "toggle_pane")
        # show all 4 panes
        self.panes_all
        # demo stacks todo delete
        self.init_stacks()

    def on_toggle_pane(self, button: Optional[Gtk.Button] = None) -> None:
        """toggle sidepane visibility"""
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)

    def setup_hotkeys(self):
        """register additional hotkeys"""
        self._hotkeys.register_hotkey("h", self.show_help)
        self._hotkeys.register_hotkey("s", self.on_toggle_pane)
        self._hotkeys.register_hotkey("shift+exclam", self.panes_single)
        self._hotkeys.register_hotkey("shift+quotedbl", self.panes_double)
        self._hotkeys.register_hotkey("shift+numbersign", self.panes_triple)
        self._hotkeys.register_hotkey("shift+dollar", self.panes_all)
        self._hotkeys.register_hotkey("Up", self.obc_arrow_up)
        self._hotkeys.register_hotkey("Down", self.obc_arrow_dn)
        self._hotkeys.register_hotkey("Left", self.obc_arrow_l)
        self._hotkeys.register_hotkey("Right", self.obc_arrow_r)
        # call helper function
        self._hotkeys.register_hotkey("n", lambda: self.on_time_now())
        self._hotkeys.register_hotkey(
            "e",
            lambda gesture, n_press, x, y: _event_selection(
                self,
                gesture,
                n_press,
                x,
                y,
                "event one" if self._app.selected_event == "event two" else "event two",
            ),
        )

    # hotkey action functions
    def show_help(self):
        self._notify.debug(
            "manual\n"
            "\nhover mouse over buttons & text = show tooltips"
            "\nhover mouse over notification message = do not hide message"
            "\nright-click = context menu : change pane content & access settings etc"
            "\nesc : discard message\n\nhotkeys (hk)"
            "\nh : show help (this message)"
            "\ns : toggle side pane"
            "\ne : toggle selected event for change time"
            "\narrow keys : up/down = change period | left/right = change time"
            "\n\tfor selected event"
            "\nn : set time now for selected event location"
            "\n\t(your computer > utc > event location time)"
            "\ntab/shift+tab : navigate between widgets in side pane"
            "\nspace/enter : activate button / dropdown when focused"
            "\nshift+1/2/3/4 : show single / double / triple / all panes"
            "\n\nnote : if entry / text field is focused, hotkeys will not work"
            "\n\t(text field will 'consume' key press)"
            "\n\nrecommended workflow :"
            "\nenter event 1 data = calculate event / birth chart"
            "\nif you want transit / progression etc (aka event 2) :"
            "\n\tenter date-time 2 (use event 1 location & name)"
            "\n\tenter location 2 for relocation event"
            "\n\tenter custom name 2 (ie 'marriage') = save event 2 linked to event 1"
            "\ndelete date-time 2 = erase event 2 data (not interested in transit etc)"
            "\nnote : event name / title will be used for file saving",
            source="help",
            timeout=5,
            route=["user"],
        )

    def init_stacks(self):
        """initialize stacks with content"""
        positions_ = self._swe_positions.calculate_positions()
        self._notify.debug(
            f"positions : {positions_}",
            source="positions",
            route=["terminal"],
        )
        # some example content for each stack
        # todo only need 1 stack & share it with 4 switchers
        panes = ["top-left", "top-right", "bottom-left", "bottom-right"]
        for pane in panes:
            # create stack for each position
            stack = self.get_stack(pane)
            if not stack:
                continue
            old_stack = stack.get_child_by_name("tables")
            if old_stack:
                stack.remove(old_stack)
                page = self._swe_positions.positions_page()
                stack.add_titled(page, "positions", "positions")
            if stack:
                # test labels todo pages here please thank you
                label1 = Gtk.Label(label="astrology chart")
                label1.add_css_class("label-tl")
                label2 = Gtk.Label(label="text editor")
                label2.add_css_class("label-tr")
                label3 = Gtk.Label(label="data graph")
                label3.add_css_class("label-bl")
                label4 = Gtk.Label(label="calculation results")
                label4.add_css_class("label-br")

                stack.add_titled(label1, "chart", "-chart")
                stack.add_titled(label2, "editor", "-editor")
                stack.add_titled(label3, "data", "-data")
                stack.add_titled(label4, "tables", "-tables")
                # set stack as child of frame
                frame = getattr(self, f"frm_{pane.replace('-', '_')}", None)
                if frame:
                    # frame.present()
                    frame.set_child(stack)

    # panes show single
    def panes_single(self) -> None:
        """show single pane : bottom right
        shift+single-click / shift+1"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(0)

    # panes show 2
    def panes_double(self) -> None:
        """show & center bottom 2 panes (hide top 2)
        shift+double-click / shift+2"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            # separator position in pixels, from top-left | -ve = unset | default 0
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)

    # panes show 3
    def panes_triple(self) -> None:
        """show & center top 2 panes & bottom single
        shift+triple-click / shift+3"""
        if (
            hasattr(self, "pnd_main_v")
            and hasattr(self, "pnd_top_h")
            and hasattr(self, "pnd_btm_h")
        ):
            self.pnd_main_v.set_position(self.pnd_main_v.get_height() // 2)
            self.pnd_top_h.set_position(self.pnd_top_h.get_width() // 2)
            self.pnd_btm_h.set_position(0)

    # panes show all 4
    def panes_all(self) -> None:
        """show & center all 4 main panes
        shift+quadruple-click / shift+4"""
        if (
            hasattr(self, "pnd_main_v")
            and hasattr(self, "pnd_top_h")
            and hasattr(self, "pnd_btm_h")
        ):
            self.pnd_main_v.set_position(self.pnd_main_v.get_height() // 2)
            self.pnd_top_h.set_position(self.pnd_top_h.get_width() // 2)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)
