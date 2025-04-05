# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Any, Optional
from .contextmanager import ContextManager
from .sidepane.sidepane import SidePaneManager
from .uisetup import UISetup
from .hotkeymanager import HotkeyManager
from ui.helpers import _on_time_now, _event_selection
from ui.mainpanes.panemanager import PaneManager


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
        PaneManager.__init__(self)
        self._app = self.get_application() or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
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
        # demo stacks todo delete
        self.init_stacks()

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
        self._hotkeys.register_hotkey("shift+exclam", self.panes_single)
        self._hotkeys.register_hotkey("shift+quotedbl", self.panes_double)
        self._hotkeys.register_hotkey("shift+numbersign", self.panes_all)
        self._hotkeys.register_hotkey("Up", self.obc_arrow_up)
        self._hotkeys.register_hotkey("Down", self.obc_arrow_dn)
        self._hotkeys.register_hotkey("Left", self.obc_arrow_l)
        self._hotkeys.register_hotkey("Right", self.obc_arrow_r)
        # call helper function
        self._hotkeys.register_hotkey("n", lambda: _on_time_now(self))
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
            "\nshift+1/2/3 : show single / double / all panes"
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

    # def create_demo_stacks(self):
    #     """create example stacks for demonstation"""
    #     positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
    #     stack_types = ["charts", "tables", "editor", "info"]

    #     for position in positions:
    #         # create chart stack with pages
    #         charts_stack = self.setup_stacks(position, "charts")
    #         label1 = Gtk.Label(label="natal chart")
    #         label2 = Gtk.Label(label="transit chart")
    #         charts_stack.add_titled(label1, "natal", "natal")
    #         charts_stack.add_titled(label2, "transit", "transit")
    #         # create tables stack with pages
    #         tables_stack = self.setup_stacks(position, "tables")
    #         label3 = Gtk.Label(label="planets table")
    #         label4 = Gtk.Label(label="houses table")
    #         tables_stack.add_titled(label3, "planets", "planets")
    #         tables_stack.add_titled(label4, "houses", "houses")
    #         # more stacks as needed
    #         editor_stack = self.setup_stacks(position, "editor")
    #         text_view = Gtk.TextView()
    #         text_view.set_wrap_mode(Gtk.WrapMode.WORD)
    #         text_view.get_buffer().set_text("notes here")
    #         editor_stack.add_titled(text_view, "editor", "editor")

    def init_stacks(self):
        """initialize stacks with content"""
        # some example content for each stack
        for position in ["top-left", "top-right", "bottom-left", "bottom-right"]:
            # create stack for each position
            stack = self.get_stack(position)
            if stack:
                # make charts stack default visible one
                label1 = Gtk.Label(label="natal chart")
                label2 = Gtk.Label(label="transit chart")
                label3 = Gtk.Label(label="planets table")

                stack.add_titled(label1, "chart", "chart")
                stack.add_titled(label2, "transit", "transit")
                stack.add_titled(label3, "planets", "planets")
                # add text editor
                text_view = Gtk.TextView()
                text_view.set_wrap_mode(Gtk.WrapMode.WORD)
                text_view.get_buffer().set_text("notes here")
                stack.add_titled(text_view, "editor", "editor")
                # set stack as child of frame
                frame = getattr(self, f"frm_{position.replace('-', '_')}", None)
                if frame and frame.get_child():
                    overlay = frame.get_child()
                    overlay.set_child(stack)

    # panes show all
    def panes_all(self) -> None:
        """show & center all 4 main panes"""
        if (
            hasattr(self, "pnd_main_v")
            and hasattr(self, "pnd_top_h")
            and hasattr(self, "pnd_btm_h")
        ):
            self.pnd_main_v.set_position(self.pnd_main_v.get_height() // 2)
            self.pnd_top_h.set_position(self.pnd_top_h.get_width() // 2)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)

    # panes show 2
    def panes_double(self) -> None:
        """show & center bottom 2 panes (hide top 2)"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            # separator position in pixels, from top-left | -ve = unset | def 0
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)

    # panes show single pane : shift-triple-click / shift+1
    def panes_single(self) -> None:
        """show single pane : bottom right"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(0)
