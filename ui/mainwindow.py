# ui/mainwindow.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Any, Optional

from .sidepane.sidepane import SidepaneManager
from .sidepane.panelsettings import update_chart_setting_checkbox
from .uisetup import UISetup
from .hotkeymanager import HotkeyManager
from ui.helpers import _event_selection
from ui.mainpanes.panetables import draw_tables
from ui.mainpanes.panechart.astrochart import AstroChart
from ui.mainpanes.datagraph import DataGraph
from sweph.calculations.positions import connect_signals_positions
from sweph.calculations.houses import connect_signals_houses
from sweph.calculations.stars import connect_signals_stars
from sweph.calculations.aspects import connect_signals_aspects


class MainWindow(
    Gtk.ApplicationWindow,
    SidepaneManager,
    UISetup,
):
    """main application window, combining ui : sidepane & main panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window"""
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        SidepaneManager.__init__(self, app=self.get_application())
        self.app = self.get_application() or Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # custom info in window title bar
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_title_buttons(True)
        self.set_titlebar(self.headerbar)
        # widget for text align left
        self.title_label = Gtk.Label(label="astrogt")
        self.headerbar.set_title_widget(self.title_label)
        self.set_default_size(800, 600)
        # setup ui : side pane
        self.setup_revealer()
        self.setup_css()
        # 4 resizable panes for charts & tables etc
        self.setup_main_panes()
        # hotkey manager
        self._hotkeys = HotkeyManager(self)
        self.setup_hotkeys()
        # intercept toggle pane button
        self._hotkeys.intercept_button_controller(self.btn_toggle_pane, "toggle_pane")
        # connect signals
        connect_signals_positions(self.get_application().signal_manager)
        connect_signals_houses(self.get_application().signal_manager)
        connect_signals_stars(self.get_application().signal_manager)
        connect_signals_aspects(self.get_application().signal_manager)
        # 4 main panes
        self.init_panes()

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
        # call helper function for time now
        self._hotkeys.register_hotkey("n", lambda: self.on_time_now())
        # toggle selected event
        self._hotkeys.register_hotkey(
            "e",
            lambda gesture, n_press, x, y: _event_selection(
                self,
                gesture,
                n_press,
                x,
                y,
                "event one" if self.app.selected_event == "event two" else "event two",
            ),
        )
        self._hotkeys.register_hotkey(
            "g", lambda: self.toggle_chart_setting("enable glyphs")
        )
        self._hotkeys.register_hotkey(
            "a", lambda: self.toggle_chart_setting("fixed asc")
        )

    def toggle_chart_setting(self, setting):
        """hotkey callback to toggle chart setting"""
        current_val = self.app.chart_settings.get(setting, False)
        new_val = not current_val
        self.app.chart_settings[setting] = new_val
        # update checkbox
        update_chart_setting_checkbox(self, setting, new_val)
        self.app.signal_manager._emit("settings_changed", None)
        self.notify.debug(
            f"toggled {setting} : {new_val}",
            source="mainwindow",
            route=["none"],
        )

    # hotkey action functions
    def show_help(self):
        self.notify.debug(
            "manual\n"
            "\nhover mouse over buttons & text = show tooltips"
            "\nhover mouse over notification message = do not hide message"
            "\nright-click = context menu : change pane content & access settings etc"
            "\nesc : discard notification message"
            "\n\nrecommended workflow :"
            "\nenter event 1 data = calculate event / birth chart"
            "\nif you want transit / progression (aka event 2) :"
            "\n\tenter date-time 2 (use event 1 location & name)"
            "\n\tenter location 2 for relocation event (transit will be for location 2)"
            "\n\tenter custom name 2 (ie 'marriage') = save event 2 linked to event 1"
            "\ndelete date-time 2 = erase event 2 data (not interested in transit etc)"
            "\nnote : event name / title will be used for file saving"
            "\n\nhotkeys (hk)"
            "\nh : show help (this message)"
            "\ns : toggle side pane"
            "\ne : toggle selected event for change time"
            "\narrow keys : up/down = change period | left/right = change time"
            "\n\tfor selected event"
            "\nn : set time now for selected event location"
            "\n\t(your computer > utc > event location time)"
            "\ntab/shift+tab : navigate between widgets in side pane"
            "\nspace/enter : activate button / dropdown when focused"
            "\nghift+1/2/3 : show single / double / triple"
            "\n\nnote : if entry / text field is focused, hotkeys will not work"
            "\na : toggle zodiac rotation (ascendant vs ari 0° at left)"
            "\ng : toggle glyphs visibility"
            "\n\nnote : if entry / text field is focused, hotkeys will not work"
            "\n\t(text field will 'consume' key press)",
            source="help",
            timeout=5,
            route=["user"],
        )

    def update_main_title(self, change_time=None):
        """show selected event & its datetime in main titlebar"""
        event = self.app.selected_event
        dt = None
        if event == "event one":
            dt = self.app.e1_chart.get("datetime")
        elif event == "event two":
            dt = self.app.e2_chart.get("datetime")
        title = "astrogt"
        if event and dt:
            title += f" | {event} : {dt}"
        elif event:
            title += f" | {event}"
        if change_time:
            title += f" | ct : {change_time}"
        elif change_time is None:
            title += " | ct : 1 day"
        self.title_label.set_text(title)

    def init_panes(self):
        """initialize panes with content"""
        # 4 main panes
        self.astro_chart = AstroChart()
        self.tables = draw_tables()
        self.tables2 = draw_tables()
        self.datagraph = DataGraph()
        widgets = {
            "bottom_right": self.astro_chart,
            "bottom_left": self.tables,
            "top_right": self.datagraph,
            "top_left": self.tables2,
        }
        for k, v in widgets.items():
            frame = getattr(self, f"frm_{k}", None)
            if frame:
                frame.set_child(v)
        # show panes
        self.panes_single()

    # panes show single
    def panes_single(self) -> None:
        """show single pane : bottom left
        shift+single-click / shift+1"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            # separator position in pixels, from top-left | -ve = unset | default 0
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(0)

    # panes show 2
    def panes_double(self) -> None:
        """show & center bottom 2 panes (hide top 2)
        shift+double-click / shift+2"""
        if hasattr(self, "pnd_main_v") and hasattr(self, "pnd_btm_h"):
            self.pnd_main_v.set_position(0)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)

    # panes show 3
    def panes_triple(self) -> None:
        """show & center top single & bottom 2 panes
        shift+triple-click / shift+3"""
        if (
            hasattr(self, "pnd_main_v")
            and hasattr(self, "pnd_top_h")
            and hasattr(self, "pnd_btm_h")
        ):
            self.pnd_main_v.set_position(self.pnd_main_v.get_height() // 2)
            self.pnd_top_h.set_position(0)
            self.pnd_btm_h.set_position(self.pnd_btm_h.get_width() // 2)

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
